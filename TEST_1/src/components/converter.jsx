import { useState } from "react";   //使用了React:这行代码从 react 库中导入 useState 钩子，用于在函数组件中管理状态。
// useState 允许我们定义和更新组件的状态。

import { invoke } from "@tauri-apps/api/core"; //Tauri框架 从 Tauri 的 API 库中导入 invoke 函数。
// 这个函数用于调用后端 Tauri 应用中的命令。在这个例子中，它被用来调用 convert_video 命令，以便在后端执行视频转换操作
// 实现前后端的交互

import { open } from "@tauri-apps/plugin-dialog";  //从 Tauri 的 plugin-dialog 插件中导入 open 函数。
// 这个函数用于打开本地文件选择对话框，允许用户选择文件。（文件选择浏览器）

export default function Converter() {//定义一个名为 Converter 的 React 函数组件。这个组件的功能是视频文件的选择和转换。
  const [filePath, setFilePath] = useState(""); //这里使用 useState 来定义组件的状态。
  // filePath 用来存储用户选择的视频文件的路径，setFilePath 是用来更新 filePath 状态的函数。初始化时，filePath 为空字符串。  

  async function selectFile() {   //这里定义了一个异步(与同步区分)函数 selectFile，用于处理文件选择的操作。
    console.log(谢谢);
    const selected = await open();
    console.log(selected);  // 输出选择的文件路径
    if (selected) {
      setFilePath(selected);
    } else {
      console.log("没有选择文件");
    }
  }
  async function convert() { //定义了一个异步函数 convert，用于调用后端进行文件转换的操作。
    await invoke("convert_video", { path: filePath }); //使用 invoke() 函数调用 Tauri 后端的 convert_video 命令，传递 filePath 作为参数。
    // 这个命令在 Tauri 后端会执行视频格式转换的操作。
  }

  return ( //这里是组件的返回部分，React 组件需要返回 JSX（HTML-like 语法）来渲染用户界面   下面就是HTML语言 JSX作为JS的扩展格式允许在 JavaScript 代码中直接编写类似 HTML 的结构 用于声明式地描述 UI 结构。
    <div> 
      <button onClick={selectFile}>选择文件</button> {/* 按钮元素 点击时会调用 selectFile 函数，打开文件选择对话框。按钮显示文本是 "选择文件" */}
      <button onClick={convert}>开始转换</button>
      <button>开始转换</button>
      <head> FUCK </head>
    </div>
  );
}
