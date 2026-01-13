import React from 'react';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import FileUpload from './components/FileUpload';
import 'antd/dist/reset.css';
import './App.css';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <div className="App">
        <FileUpload />
      </div>
    </ConfigProvider>
  );
}

export default App;
