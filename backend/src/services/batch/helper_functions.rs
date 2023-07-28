use std::{str::FromStr, path::{Path, PathBuf}};

use calamine::DataType;
use chrono::{DateTime, Utc};

pub fn value_to_bool(value: &DataType) -> Option<bool> {
    value.get_bool()
}

pub fn value_to_string(value: &DataType) -> Option<String> {
    match value.get_string() {
        None => None,
        Some(str) => Some(str.to_string()),
    }
}

pub fn value_to_i32(value: &DataType) -> Option<i32> {
    match value.as_i64() {
        None => None,
        Some(v) => Some(v as i32),
    }
}

pub fn value_to_file_path(value: &DataType, required_files: &mut Vec<PathBuf>, base_file_path: &Path) -> Option<String> {
    match value.get_string() {
        None => None,
        Some(str) => {
            let mut path = base_file_path.clone().to_path_buf();
            path.push(str);
            required_files.push(path);
            Some(str.to_string())
        }
    }
}

pub fn value_to_vec<T: FromStr>(value: &DataType) -> Option<Vec<T>> {
    value.as_string().and_then(|str| {
        Some(
            str.split(',')
                .filter_map(|x| x.parse::<T>().ok())
                .collect::<Vec<T>>(),
        )
    })
}

pub fn value_to_chrono_date(value: &DataType) -> Option<DateTime<Utc>> {
    value
        .as_datetime()
        .and_then(|naive_dt| Some(naive_dt.and_utc()))
}
