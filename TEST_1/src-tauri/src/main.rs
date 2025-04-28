// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command;
use std::path::Path;

#[tauri::command]
fn convert_video(input_path: String, output_format: String) -> Result<String, String> {
    let input = Path::new(&input_path);
    let parent = input.parent().ok_or("无法获取文件目录")?;
    let stem = input.file_stem().ok_or("无法获取文件名")?;

    let output_path = parent.join(format!(
        "{}_converted.{}",
        stem.to_string_lossy(),
        output_format
    ));

    let status = Command::new("ffmpeg")
        .args(["-i", input_path.as_str(), output_path.to_str().unwrap()])
        .status()
        .map_err(|e| format!("调用 ffmpeg 出错: {}", e))?;

    if status.success() {
        Ok(output_path.to_string_lossy().to_string())
    } else {
        Err("转换失败，请检查 ffmpeg 是否可用".to_string())
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![convert_video])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
