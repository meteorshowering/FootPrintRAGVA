import { createApp } from 'vue';   // 从 vue 导入 createApp
// import App from './App.vue';
import store from './store';         // 导入你的 Vuex store
import App from './App.vue';
import './assets/global.css';       // 导入全局样式

createApp(App)                     // 使用 createApp 来创建应用实例
  .use(store)                      // 使用 Vuex store
  .mount('#app');                  // 挂载应用到 DOM 元素上
