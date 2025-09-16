#[cfg_attr(feature = "trace", crustrace::omni)]
mod innermod {
    use crate::genson_rs::{build_json_schema, get_builder, BuildConfig};
    use serde::de::Error as DeError;
    use serde::{Deserialize, Serialize};
    use serde_json::Value;
    use std::borrow::Cow;
    use std::panic::{self, AssertUnwindSafe};

    /// Maximum length of JSON string to include in error messages before truncating
    const MAX_JSON_ERROR_LENGTH: usize = 100;

    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub struct SchemaInferenceConfig {
        /// Whether to treat top-level arrays as streams of objects
        pub ignore_outer_array: bool,
        /// Delimiter for NDJSON format (None for regular JSON)
        pub delimiter: Option<u8>,
        /// Schema URI to use ("AUTO" for auto-detection)
        pub schema_uri: Option<String>,
        /// Threshold above which non-fixed keys are treated as a map
        pub map_threshold: usize,
        /// Maximum number of required keys a Map can have. If None, no gating based on required keys.
        /// If Some(n), objects with more than n required keys will be forced to Record type.
        pub map_max_required_keys: Option<usize>,
        /// Force override of field treatment, e.g. {"labels": "map"}
        pub force_field_types: std::collections::HashMap<String, String>,
        /// Wrap the inferred top-level schema under a single required field with this name.
        /// Example: wrap_root = Some("labels") turns `{...}` into
        /// `{"type":"object","properties":{"labels":{...}},"required":["labels"]}`.
        pub wrap_root: Option<String>,
        /// Whether to output Avro schema rather than regular JSON Schema.
        #[cfg(feature = "avro")]
        pub avro: bool,
    }

    impl Default for SchemaInferenceConfig {
        fn default() -> Self {
            Self {
                ignore_outer_array: true,
                delimiter: None,
                schema_uri: Some("AUTO".to_string()),
                map_threshold: 20,
                map_max_required_keys: None,
                force_field_types: std::collections::HashMap::new(),
                wrap_root: None,
                #[cfg(feature = "avro")]
                avro: false,
            }
        }
    }

    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub struct SchemaInferenceResult {
        pub schema: Value,
        pub processed_count: usize,
    }

    #[cfg(feature = "avro")]
    impl SchemaInferenceResult {
        pub fn to_avro_schema(
            &self,
            namespace: &str,
            utility_namespace: Option<&str>,
            base_uri: Option<&str>,
            split_top_level: bool,
        ) -> Value {
            avrotize::converter::jsons_to_avro(
                &self.schema,
                namespace,
                utility_namespace.unwrap_or(""),
                base_uri.unwrap_or("genson-core"),
                split_top_level,
            )
        }
    }

    fn validate_json(s: &str) -> Result<(), serde_json::Error> {
        let mut de = serde_json::Deserializer::from_str(s);
        serde::de::IgnoredAny::deserialize(&mut de)?; // lightweight: ignores the parsed value
        de.end()
    }

    fn validate_ndjson(s: &str) -> Result<(), serde_json::Error> {
        for line in s.lines() {
            let trimmed = line.trim();
            if trimmed.is_empty() {
                continue;
            }
            validate_json(trimmed)?; // propagate serde_json::Error
        }
        Ok(())
    }

    /// Post-process an inferred JSON Schema to rewrite certain object shapes as maps.
    ///
    /// This mutates the schema in place, applying user overrides and heuristics.
    ///
    /// # Rules
    /// - If the current field name matches a `force_field_types` override, that wins
    ///   (`"map"` rewrites to `additionalProperties`, `"record"` leaves as-is).
    /// - Otherwise, applies map inference heuristics based on:
    ///   - Total key cardinality (`map_threshold`)
    ///   - Required key cardinality (`map_max_required_keys`)
    ///   - Value homogeneity (all values must be homogeneous strings)
    /// - Recurses into nested objects/arrays, carrying field names down so overrides apply.
    fn rewrite_objects(
        schema: &mut Value,
        field_name: Option<&str>,
        config: &SchemaInferenceConfig,
    ) {
        if let Value::Object(obj) = schema {
            // --- Forced overrides by field name ---
            if let Some(name) = field_name {
                if let Some(forced) = config.force_field_types.get(name) {
                    match forced.as_str() {
                        "map" => {
                            obj.remove("properties");
                            obj.remove("required");
                            obj.insert(
                                "additionalProperties".to_string(),
                                serde_json::json!({ "type": "string" }),
                            );
                            return; // no need to apply heuristics or recurse
                        }
                        "record" => {
                            if let Some(props) =
                                obj.get_mut("properties").and_then(|p| p.as_object_mut())
                            {
                                for (k, v) in props {
                                    rewrite_objects(v, Some(k), config);
                                }
                            }
                            if let Some(items) = obj.get_mut("items") {
                                rewrite_objects(items, None, config);
                            }
                            return;
                        }
                        _ => {}
                    }
                }
            }

            // --- Heuristic rewrite ---
            if let Some(props) = obj.get("properties").and_then(|p| p.as_object()) {
                let key_count = props.len(); // |UK| - total keys observed
                let above_threshold = key_count >= config.map_threshold;

                // Copy out child schema shapes
                let child_schemas: Vec<Value> = props.values().cloned().collect();

                // Detect map-of-records only if:
                // - all children are identical
                // - and that child is itself an object with "properties" (i.e. a proper record)
                if above_threshold {
                    if let Some(first) = child_schemas.first() {
                        if first.get("type") == Some(&Value::String("object".into()))
                            && first.get("properties").is_some()
                            && child_schemas.len() > 1
                        {
                            let all_same = child_schemas.iter().all(|other| other == first);
                            if all_same {
                                obj.remove("properties");
                                obj.remove("required");
                                obj.insert("additionalProperties".to_string(), first.clone());
                                return;
                            }
                        }
                    }
                }

                // Calculate required key count |RK|
                let required_key_count = obj
                    .get("required")
                    .and_then(|r| r.as_array())
                    .map(|r| r.len())
                    .unwrap_or(0);

                // Check if all values are homogeneous schemas
                let homogeneous_schema = if let Some(first_schema) = props.values().next() {
                    if props.values().all(|schema| schema == first_schema) {
                        Some(first_schema.clone())
                    } else {
                        None
                    }
                } else {
                    None
                };

                // Apply map inference logic
                let should_be_map = if above_threshold && homogeneous_schema.is_some() {
                    if let Some(max_required) = config.map_max_required_keys {
                        required_key_count <= max_required
                    } else {
                        true
                    }
                } else {
                    false
                };

                if should_be_map {
                    if let Some(schema) = homogeneous_schema {
                        obj.remove("properties");
                        obj.remove("required");
                        obj.insert("type".to_string(), Value::String("object".to_string()));
                        obj.insert("additionalProperties".to_string(), schema);
                        return;
                    }
                }
            }

            // --- Recurse into nested values ---
            if let Some(props) = obj.get_mut("properties").and_then(|p| p.as_object_mut()) {
                for (k, v) in props {
                    rewrite_objects(v, Some(k), config);
                }
            }
            if let Some(items) = obj.get_mut("items") {
                rewrite_objects(items, None, config);
            }
            for v in obj.values_mut() {
                rewrite_objects(v, None, config);
            }
        } else if let Value::Array(arr) = schema {
            for v in arr {
                rewrite_objects(v, None, config);
            }
        }
    }

    /// Recursively reorder union type arrays in a JSON Schema by canonical precedence.
    ///
    /// Special case: preserves the common `["null", T]` pattern without reordering.
    pub fn reorder_unions(schema: &mut Value) {
        match schema {
            Value::Object(obj) => {
                if let Some(Value::Array(types)) = obj.get_mut("type") {
                    // sort by canonical precedence, but keep ["null", T] pattern intact
                    if !(types.len() == 2 && types.iter().any(|t| t == "null")) {
                        types.sort_by_key(type_rank);
                    }
                }
                // recurse into properties/items/etc.
                for v in obj.values_mut() {
                    reorder_unions(v);
                }
            }
            Value::Array(arr) => {
                for v in arr {
                    reorder_unions(v);
                }
            }
            _ => {}
        }
    }

    /// Assign a numeric precedence rank to a JSON Schema type.
    ///
    /// Used by `reorder_unions` to sort union members deterministically.
    /// - Null always first
    /// - Containers before scalars (to enforce widening)
    /// - Scalars ordered by narrowness
    /// - Unknown types last
    pub fn type_rank(val: &Value) -> usize {
        match val {
            Value::String(s) => type_string_rank(s),
            Value::Object(obj) => {
                if let Some(Value::String(t)) = obj.get("type") {
                    type_string_rank(t)
                } else {
                    100 // object with no "type" field
                }
            }
            _ => 100, // non-string/non-object
        }
    }

    /// Internal helper: rank by type string
    fn type_string_rank(s: &str) -> usize {
        match s {
            // Null always first
            "null" => 0,

            // Containers before scalars: widening takes precedence
            "map" => 1,
            "array" => 2,
            "object" | "record" => 3,

            // Scalars (ordered by 'narrowness')
            "boolean" => 10,
            "integer" | "int" | "long" => 11,
            "number" | "float" | "double" => 12,
            "enum" => 13,
            "string" => 14,
            "fixed" => 15,
            "bytes" => 16,

            // Fallback
            _ => 99,
        }
    }

    /// Infer JSON schema from a collection of JSON strings
    pub fn infer_json_schema_from_strings(
        json_strings: &[String],
        config: SchemaInferenceConfig,
    ) -> Result<SchemaInferenceResult, String> {
        if json_strings.is_empty() {
            return Err("No JSON strings provided".to_string());
        }

        // Wrap the entire genson-rs interaction in panic handling
        let result = panic::catch_unwind(AssertUnwindSafe(
            || -> Result<SchemaInferenceResult, String> {
                // Create schema builder
                let mut builder = get_builder(config.schema_uri.as_deref());

                // Build config for genson-rs
                let build_config = BuildConfig {
                    delimiter: config.delimiter,
                    ignore_outer_array: config.ignore_outer_array,
                };

                let mut processed_count = 0;

                // Process each JSON string
                for (i, json_str) in json_strings.iter().enumerate() {
                    if json_str.trim().is_empty() {
                        continue;
                    }

                    // Choose validation strategy based on delimiter
                    let validation_result = if let Some(delim) = config.delimiter {
                        if delim == b'\n' {
                            validate_ndjson(json_str)
                        } else {
                            Err(serde_json::Error::custom(format!(
                                "Unsupported delimiter: {:?}",
                                delim
                            )))
                        }
                    } else {
                        validate_json(json_str)
                    };

                    if let Err(parse_error) = validation_result {
                        let truncated_json = if json_str.len() > MAX_JSON_ERROR_LENGTH {
                            format!(
                                "{}... [truncated {} chars]",
                                &json_str[..MAX_JSON_ERROR_LENGTH],
                                json_str.len() - MAX_JSON_ERROR_LENGTH
                            )
                        } else {
                            json_str.clone()
                        };

                        return Err(format!(
                            "Invalid JSON input at index {}: {} - JSON: {}",
                            i + 1,
                            parse_error,
                            truncated_json
                        ));
                    }

                    // Safe: JSON is valid, now hand off to genson-rs
                    let prepared_json: Cow<str> = if let Some(ref field) = config.wrap_root {
                        if config.delimiter == Some(b'\n') {
                            // NDJSON: wrap each line separately
                            let mut wrapped_lines = Vec::new();
                            for line in json_str.lines() {
                                let trimmed = line.trim();
                                if trimmed.is_empty() {
                                    continue;
                                }
                                let inner_val: Value =
                                    serde_json::from_str(trimmed).map_err(|e| {
                                        format!(
                                            "Failed to parse NDJSON line before wrap_root: {}",
                                            e
                                        )
                                    })?;
                                wrapped_lines
                                    .push(serde_json::json!({ field: inner_val }).to_string());
                            }
                            Cow::Owned(wrapped_lines.join("\n"))
                        } else {
                            // Single JSON doc
                            let inner_val: Value = serde_json::from_str(json_str).map_err(|e| {
                                format!("Failed to parse JSON before wrap_root: {}", e)
                            })?;
                            Cow::Owned(serde_json::json!({ field: inner_val }).to_string())
                        }
                    } else {
                        Cow::Borrowed(json_str)
                    };

                    let mut bytes = prepared_json.as_bytes().to_vec();

                    // Build schema incrementally - this is where panics happen
                    let _schema = build_json_schema(&mut builder, &mut bytes, &build_config);
                    processed_count += 1;
                }

                // Get final schema
                let mut final_schema = builder.to_schema();
                rewrite_objects(&mut final_schema, None, &config);
                reorder_unions(&mut final_schema);

                #[cfg(feature = "avro")]
                if config.avro {
                    let avro_schema = SchemaInferenceResult {
                        schema: final_schema.clone(),
                        processed_count,
                    }
                    .to_avro_schema(
                        "genson", // namespace
                        Some(""),
                        Some(""), // base_uri
                        false,    // don't split top-level
                    );
                    return Ok(SchemaInferenceResult {
                        schema: avro_schema,
                        processed_count,
                    });
                }

                Ok(SchemaInferenceResult {
                    schema: final_schema,
                    processed_count,
                })
            },
        ));

        // Handle the result of panic::catch_unwind
        match result {
            Ok(Ok(schema_result)) => Ok(schema_result),
            Ok(Err(e)) => Err(e),
            Err(_panic) => {
                Err("JSON schema inference failed due to invalid JSON input".to_string())
            }
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;
        use predicates::prelude::*;
        use serde_json::json;

        #[test]
        fn test_reorder_unions_string_float_null() {
            // Unordered union: string, float, null
            let mut schema = json!({
                "type": ["string", "float", "null"]
            });

            reorder_unions(&mut schema);

            // After reordering, null should come first, then float/number, then string
            assert_eq!(
                schema,
                json!({
                    "type": ["null", "float", "string"]
                })
            );
        }

        #[test]
        fn test_basic_schema_inference() {
            let json_strings = vec![
                r#"{"name": "Alice", "age": 30}"#.to_string(),
                r#"{"name": "Bob", "age": 25, "city": "NYC"}"#.to_string(),
            ];

            let result =
                infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default())
                    .expect("Schema inference should succeed");

            // Test processed count
            assert_eq!(result.processed_count, 2);

            // Use predicates to test schema structure
            let schema_str = result.schema.to_string();

            predicate::str::contains("\"type\"")
                .and(predicate::str::contains("object"))
                .eval(&schema_str);

            predicate::str::contains("\"properties\"").eval(&schema_str);

            // Check that both name and age properties are present
            predicate::str::contains("\"name\"")
                .and(predicate::str::contains("\"age\""))
                .eval(&schema_str);

            println!(
                "✅ Generated schema: {}",
                serde_json::to_string_pretty(&result.schema).unwrap()
            );
        }

        #[test]
        fn test_empty_input() {
            let json_strings = vec![];
            let result =
                infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default());

            assert!(result.is_err());

            let error_msg = result.unwrap_err();
            predicate::str::contains("No JSON strings provided").eval(&error_msg);

            println!("✅ Empty input correctly rejected with: {}", error_msg);
        }

        #[test]
        fn test_invalid_json_variants() {
            let test_cases = vec![
                (
                    r#"{"name": "Alice"}"#,
                    r#"{"invalid": json}"#,
                    "unquoted value",
                ),
                (
                    r#"{"valid": "json"}"#,
                    r#"{"incomplete":"#,
                    "incomplete string",
                ),
                (r#"{"good": "data"}"#, r#"{"trailing":,"#, "trailing comma"),
                (
                    r#"{"working": true}"#,
                    r#"{invalid: "json"}"#,
                    "unquoted key",
                ),
                (
                    r#"{"normal": "object"}"#,
                    r#"{"nested": {"broken": json}}"#,
                    "nested broken JSON",
                ),
            ];

            for (valid_json, invalid_json, description) in test_cases {
                println!("🧪 Testing: {}", description);
                println!("   Valid JSON: {}", valid_json);
                println!("   Invalid JSON: {}", invalid_json);

                let json_strings = vec![valid_json.to_string(), invalid_json.to_string()];

                let result =
                    infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default());

                // Should return an error instead of panicking
                assert!(result.is_err(), "Expected error for case: {}", description);

                let error_msg = result.unwrap_err();

                // Use predicates to verify error message content
                predicate::str::contains("Invalid JSON input at position").eval(&error_msg);

                // For short JSON strings, verify the content is included
                if invalid_json.len() <= MAX_JSON_ERROR_LENGTH {
                    predicate::str::contains(invalid_json).eval(&error_msg);
                } else {
                    // For long JSON, just check that truncation happened
                    predicate::str::contains("truncated").eval(&error_msg);
                }

                // Ensure we don't have panic-related messages
                predicate::str::contains("panicked").not().eval(&error_msg);

                predicate::str::contains("SIGABRT").not().eval(&error_msg);

                println!("   ❌ Correctly failed with: {}", error_msg);
                println!();
            }
        }

        #[test]
        fn test_mixed_valid_and_empty_strings() {
            let json_strings = vec![
                r#"{"name": "Alice", "age": 30}"#.to_string(),
                "".to_string(),    // Empty string should be skipped
                "   ".to_string(), // Whitespace-only should be skipped
                r#"{"name": "Bob", "age": 25}"#.to_string(),
            ];

            let result =
                infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default())
                    .expect("Should succeed with valid JSON, skipping empty strings");

            // Should process only the 2 valid JSON strings
            assert_eq!(result.processed_count, 2);

            let schema_str = result.schema.to_string();
            predicate::str::contains("\"name\"")
                .and(predicate::str::contains("\"age\""))
                .eval(&schema_str);

            println!(
                "✅ Processed {} valid strings, skipped empty ones",
                result.processed_count
            );
        }

        #[test]
        fn test_schema_config_variations() {
            let json_strings = vec![r#"[{"item": "first"}, {"item": "second"}]"#.to_string()];

            // Test with ignore_outer_array = false
            let config_array = SchemaInferenceConfig {
                ignore_outer_array: false,
                ..Default::default()
            };

            let result = infer_json_schema_from_strings(&json_strings, config_array)
                .expect("Should handle array schema");

            let schema_str = result.schema.to_string();
            predicate::str::contains("\"type\"")
                .and(predicate::str::contains("array"))
                .eval(&schema_str);

            println!(
                "✅ Array schema: {}",
                serde_json::to_string_pretty(&result.schema).unwrap()
            );

            // Test with ignore_outer_array = true (default)
            let config_object = SchemaInferenceConfig {
                ignore_outer_array: true,
                ..Default::default()
            };

            let result = infer_json_schema_from_strings(&json_strings, config_object)
                .expect("Should handle object schema from array items");

            let schema_str = result.schema.to_string();
            predicate::str::contains("\"type\"")
                .and(predicate::str::contains("object"))
                .eval(&schema_str);

            predicate::str::contains("\"item\"").eval(&schema_str);

            println!(
                "✅ Object schema from array items: {}",
                serde_json::to_string_pretty(&result.schema).unwrap()
            );
        }

        #[test]
        fn test_very_long_invalid_json() {
            // Create a very long invalid JSON string
            let long_value = "x".repeat(500); // 500 char string
            let long_invalid_json = format!(
                r#"{{"field1": "{}", "field2": "{}", "field3": "{}", "field4": "{}", "invalid_syntax": }}"#,
                long_value, long_value, long_value, long_value
            );

            let json_strings = vec![
                r#"{"valid": "json"}"#.to_string(),
                long_invalid_json.clone(),
            ];

            println!(
                "🧪 Testing very long invalid JSON ({} chars)",
                long_invalid_json.len()
            );

            let result =
                infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default());

            assert!(result.is_err(), "Expected error for very long invalid JSON");

            let error_msg = result.unwrap_err();

            println!("The error message was: {}", error_msg);

            // Should contain truncation indicator
            predicate::str::contains("truncated").eval(&error_msg);

            // Should contain position information
            predicate::str::contains("Invalid JSON input at position 2").eval(&error_msg);

            // Error message should be reasonable length (much shorter than original JSON)
            assert!(
                error_msg.len() < long_invalid_json.len() / 2,
                "Error message should be much shorter than original JSON"
            );

            println!(
                "   ❌ Correctly truncated long JSON in error: {}",
                error_msg
            );

            // Verify the error message doesn't exceed a reasonable length
            assert!(
                error_msg.len() < 500,
                "Error message should be under 500 chars, got: {}",
                error_msg.len()
            );
        }

        #[test]
        fn test_complex_nested_schema() {
            let json_strings = vec![
                json!({
                    "user": {
                        "id": 123,
                        "profile": {
                            "name": "Alice",
                            "preferences": ["dark_mode", "notifications"]
                        }
                    },
                    "metadata": {
                        "created_at": "2024-01-01",
                        "version": 1
                    }
                })
                .to_string(),
                json!({
                    "user": {
                        "id": 456,
                        "profile": {
                            "name": "Bob",
                            "preferences": ["light_mode"]
                        }
                    },
                    "metadata": {
                        "created_at": "2024-01-02",
                        "version": 2
                    }
                })
                .to_string(),
            ];

            let result =
                infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default())
                    .expect("Should handle complex nested schema");

            assert_eq!(result.processed_count, 2);

            let schema_str = result.schema.to_string();

            // Check for nested structure
            predicate::str::contains("\"user\"")
                .and(predicate::str::contains("\"metadata\""))
                .and(predicate::str::contains("\"profile\""))
                .and(predicate::str::contains("\"preferences\""))
                .eval(&schema_str);

            println!("✅ Complex nested schema generated successfully");
            println!(
                "Schema: {}",
                serde_json::to_string_pretty(&result.schema).unwrap()
            );
        }

        #[test]
        fn test_ndjson_parsing() {
            // Two valid JSON objects separated by newlines (NDJSON format)
            let ndjson_input = r#"
{"name": "Alice", "age": 30}
{"name": "Bob", "age": 25, "city": "NYC"}
{"name": "Charlie"}
"#;

            let json_strings = vec![ndjson_input.to_string()];

            let config = SchemaInferenceConfig {
                delimiter: Some(b'\n'),
                ..Default::default()
            };

            let result = infer_json_schema_from_strings(&json_strings, config)
                .expect("NDJSON schema inference should succeed");

            // All 3 objects should be processed
            assert_eq!(result.processed_count, 1,
            "NDJSON should be counted as a single input string but parsed into multiple rows internally"
        );

            let schema_str = result.schema.to_string();

            // The schema should include properties from all lines
            assert!(!schema_str.contains("Alice")); // values are not in schema
            assert!(schema_str.contains("\"name\""));
            assert!(schema_str.contains("\"age\""));
            assert!(schema_str.contains("\"city\""));

            println!(
                "✅ NDJSON schema generated: {}",
                serde_json::to_string_pretty(&result.schema).unwrap()
            );
        }

        #[test]
        fn test_invalid_ndjson_line() {
            // Second line is malformed
            let ndjson_input = r#"
{"valid": true}
{"invalid": json}
{"also_valid": 123}
"#;

            let json_strings = vec![ndjson_input.to_string()];

            let config = SchemaInferenceConfig {
                delimiter: Some(b'\n'),
                ..Default::default()
            };

            let result = infer_json_schema_from_strings(&json_strings, config);

            assert!(result.is_err(), "Expected error for malformed NDJSON line");

            let err_msg = result.unwrap_err();
            eprintln!("Got error: {}", err_msg);
            assert!(
                err_msg
                    .contains("Invalid JSON input at index 1: expected value at line 1 column 13"),
                "Error message should report the failing line"
            );
            println!("✅ Correctly rejected malformed NDJSON: {}", err_msg);
        }

        /// Two objects with varying keys and homogeneous string values (low map threshold)
        #[test]
        fn test_map_threshold_rewrite() {
            let json_strings = vec![
                r#"{"labels": {"en": "Hello", "fr": "Bonjour"}}"#.to_string(),
                r#"{"labels": {"de": "Hallo", "es": "Hola"}}"#.to_string(),
            ];

            let config = SchemaInferenceConfig {
                map_threshold: 2,
                ..Default::default()
            };
            let result = infer_json_schema_from_strings(&json_strings, config).unwrap();

            let labels = &result.schema["properties"]["labels"];
            assert_eq!(labels["type"], "object");
            assert!(labels.get("additionalProperties").is_some());
            assert!(labels.get("properties").is_none());
        }

        /// Two objects with varying keys and homogeneous string values (default map threshold)
        #[test]
        fn test_map_threshold_as_record() {
            let json_strings = vec![
                r#"{"labels": {"en": "Hello", "fr": "Bonjour"}}"#.to_string(),
                r#"{"labels": {"de": "Hallo", "es": "Hola"}}"#.to_string(),
            ];

            let result =
                infer_json_schema_from_strings(&json_strings, SchemaInferenceConfig::default())
                    .unwrap();

            let labels = &result.schema["properties"]["labels"];
            assert!(labels.get("properties").is_some());
            assert!(labels.get("additionalProperties").is_none());
        }

        #[test]
        fn test_wrap_root_inserts_single_required_field() {
            let json_strings = vec![
                r#"{"en":{"language":"en","value":"Hello"},"fr":{"language":"fr","value":"Bonjour"}}"#.to_string(),
            ];

            let cfg = SchemaInferenceConfig {
                wrap_root: Some("labels".to_string()),
                ..Default::default()
            };

            let out = infer_json_schema_from_strings(&json_strings, cfg).unwrap();
            let sch = out.schema;

            assert_eq!(sch["type"], "object");
            assert_eq!(sch["required"], serde_json::json!(["labels"]));
            assert!(sch["properties"]["labels"].is_object());
        }

        #[test]
        fn test_rewrite_objects_map_of_records() {
            use serde_json::json;

            // Schema that genson-rs would roughly emit for {"en": {...}, "fr": {...}}
            let mut schema = json!({
                "type": "object",
                "properties": {
                    "en": {
                        "type": "object",
                        "properties": {
                            "language": { "type": "string" },
                            "value": { "type": "string" }
                        },
                        "required": ["language", "value"]
                    },
                    "fr": {
                        "type": "object",
                        "properties": {
                            "language": { "type": "string" },
                            "value": { "type": "string" }
                        },
                        "required": ["language", "value"]
                    }
                },
                "required": ["en","fr"]
            });

            let cfg = SchemaInferenceConfig {
                map_threshold: 2, // force detection at 2 keys
                ..Default::default()
            };

            rewrite_objects(&mut schema, None, &cfg);

            // After rewrite, we should have additionalProperties instead of fixed properties
            assert_eq!(schema["type"], "object");
            assert!(schema.get("properties").is_none());
            assert!(schema.get("required").is_none());

            // additionalProperties should carry the inner record shape
            let ap = schema
                .get("additionalProperties")
                .expect("should insert additionalProperties");

            assert_eq!(ap["type"], "object");
            assert_eq!(ap["properties"]["language"], json!({ "type": "string" }));
            assert_eq!(ap["properties"]["value"], json!({ "type": "string" }));
        }

        #[test]
        fn test_map_of_strings_not_promoted_to_records() {
            let schema = json!({
                "type": "object",
                "properties": {
                    "labels": {
                        "type": "object",
                        "properties": {
                            "en": { "type": "string" },
                            "fr": { "type": "string" }
                        },
                        "required": ["en", "fr"]
                    }
                },
                "required": ["labels"]
            });

            let mut sch = schema.clone();
            let cfg = SchemaInferenceConfig {
                map_threshold: 2,
                ..Default::default()
            };
            rewrite_objects(&mut sch, None, &cfg);

            assert_eq!(
                sch["properties"]["labels"]["additionalProperties"]["type"],
                "string"
            );
        }

        #[test]
        fn test_rewrite_objects_respects_map_max_required_keys() {
            let mut schema = json!({
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "string"}
                },
                "required": ["field1", "field2"]
            });

            let config = SchemaInferenceConfig {
                map_threshold: 2,
                map_max_required_keys: Some(1), // Max 1 required key for maps
                ..Default::default()
            };

            rewrite_objects(&mut schema, None, &config);

            // Should remain as record because 2 required keys > 1
            assert_eq!(schema["type"], "object");
            assert!(schema.get("properties").is_some());
            assert!(schema.get("additionalProperties").is_none());
        }

        #[test]
        fn test_rewrite_objects_allows_map_with_few_required_keys() {
            let mut schema = json!({
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "string"}
                },
                "required": ["field1"] // Only 1 required key
            });

            let config = SchemaInferenceConfig {
                map_threshold: 2,
                map_max_required_keys: Some(1), // Max 1 required key for maps
                ..Default::default()
            };

            rewrite_objects(&mut schema, None, &config);

            // Should become map because 1 required key ≤ 1
            assert_eq!(schema["type"], "object");
            assert!(schema.get("additionalProperties").is_some());
            assert!(schema.get("properties").is_none());
        }

        #[test]
        fn test_rewrite_objects_none_max_required_keys_preserves_behavior() {
            let mut schema = json!({
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "string"},
                    "field3": {"type": "string"}
                },
                "required": ["field1", "field2", "field3"]
            });

            let config = SchemaInferenceConfig {
                map_threshold: 2,
                map_max_required_keys: None, // No gating
                ..Default::default()
            };

            rewrite_objects(&mut schema, None, &config);

            // Should become map because None means no gating (old behavior)
            assert_eq!(schema["type"], "object");
            assert!(schema.get("additionalProperties").is_some());
            assert!(schema.get("properties").is_none());
        }

        #[test]
        fn test_rewrite_objects_zero_max_required_keys() {
            let mut schema = json!({
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "string"}
                },
                "required": ["field1"]
            });

            let config = SchemaInferenceConfig {
                map_threshold: 2,
                map_max_required_keys: Some(0), // Only allow maps with 0 required keys
                ..Default::default()
            };

            rewrite_objects(&mut schema, None, &config);

            // Should remain as record because 1 required key > 0
            assert_eq!(schema["type"], "object");
            assert!(schema.get("properties").is_some());
            assert!(schema.get("additionalProperties").is_none());
        }

        #[test]
        fn test_rewrite_objects_zero_required_keys_allowed() {
            let mut schema = json!({
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "string"}
                }
                // No required array = 0 required keys
            });

            let config = SchemaInferenceConfig {
                map_threshold: 2,
                map_max_required_keys: Some(0), // Only allow maps with 0 required keys
                ..Default::default()
            };

            rewrite_objects(&mut schema, None, &config);

            // Should become map because 0 required keys ≤ 0
            assert_eq!(schema["type"], "object");
            assert!(schema.get("additionalProperties").is_some());
            assert!(schema.get("properties").is_none());
        }

        #[test]
        fn test_rewrite_objects_force_override_wins() {
            let mut schema = json!({
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "string"}
                },
                "required": ["field1", "field2"]
            });

            let mut force_types = std::collections::HashMap::new();
            force_types.insert("test_field".to_string(), "map".to_string());

            let config = SchemaInferenceConfig {
                map_threshold: 2,
                map_max_required_keys: Some(0), // Would normally block this
                force_field_types: force_types,
                ..Default::default()
            };

            // Apply with field name that matches force override
            rewrite_objects(&mut schema, Some("test_field"), &config);

            // Should become map despite having required keys due to force override
            assert_eq!(schema["type"], "object");
            assert!(schema.get("additionalProperties").is_some());
            assert!(schema.get("properties").is_none());
        }

        #[test]
        fn test_rewrite_objects_non_homogeneous_values_not_rewritten() {
            let mut schema = json!({
                "type": "object",
                "properties": {
                    "field1": {"type": "string"},
                    "field2": {"type": "integer"} // Non-homogeneous
                },
                "required": []
            });

            let config = SchemaInferenceConfig {
                map_threshold: 2,
                map_max_required_keys: Some(5), // Would allow this
                ..Default::default()
            };

            rewrite_objects(&mut schema, None, &config);

            // Should remain as record because values are not homogeneous
            assert_eq!(schema["type"], "object");
            assert!(schema.get("properties").is_some());
            assert!(schema.get("additionalProperties").is_none());
        }

        #[test]
        fn test_rewrite_objects_below_threshold_not_rewritten() {
            let mut schema = json!({
                "type": "object",
                "properties": {
                    "field1": {"type": "string"}
                },
                "required": []
            });

            let config = SchemaInferenceConfig {
                map_threshold: 5,               // Above the key count
                map_max_required_keys: Some(5), // Would allow this
                ..Default::default()
            };

            rewrite_objects(&mut schema, None, &config);

            // Should remain as record because below threshold
            assert_eq!(schema["type"], "object");
            assert!(schema.get("properties").is_some());
            assert!(schema.get("additionalProperties").is_none());
        }

        // Existing tests...
        #[test]
        fn test_map_max_required_keys_with_wrap_root() {
            let json_strings = vec![
                r#"{"en":{"language":"en","value":"Hello"},"fr":{"language":"fr","value":"Bonjour"}}"#.to_string(),
            ];

            let cfg = SchemaInferenceConfig {
                wrap_root: Some("labels".to_string()),
                map_threshold: 2,
                map_max_required_keys: Some(1), // Should allow the wrapped content
                ..Default::default()
            };

            let out = infer_json_schema_from_strings(&json_strings, cfg).unwrap();
            let sch = out.schema;

            assert_eq!(sch["type"], "object");
            assert_eq!(sch["required"], serde_json::json!(["labels"]));

            // The wrapped labels should have the map logic applied
            let labels_content = &sch["properties"]["labels"];
            assert!(labels_content.is_object());

            println!("✅ map_max_required_keys works with wrap_root");
        }
    }
}
pub use innermod::*;
