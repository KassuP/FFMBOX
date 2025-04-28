// Prevents additional console window on Windows in release, DO NOT REMOVE!!
use tauri_plugin_fs::FsExt;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
fn run() {
  tauri::Builder::default()
      .plugin(tauri_plugin_fs::init())
      .setup(|app| {
          // 允许指定目录
          let scope = app.fs_scope();
          scope.allow_directory("/path/to/directory", false);
          dbg!(scope.allowed());

          Ok(())
       })
       .run(tauri::generate_context!())
       .expect("error while running tauri application");
}

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
fn main() {
    fro_back_lib::run()
}

