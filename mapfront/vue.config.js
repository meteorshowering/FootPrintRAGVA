const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      // 注意：WebSocket 连接应该直接连接，不使用代理
      // '/ws': { target: 'http://127.0.0.1:8000', ws: true },
      '/api': { target: 'http://127.0.0.1:8000' },
      '/static': { target: 'http://127.0.0.1:8000' },
      '/experiment-data': { target: 'http://127.0.0.1:8000' }
    }
  }
})
