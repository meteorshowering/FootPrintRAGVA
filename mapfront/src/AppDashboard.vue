<template>
  <div id="app">
    <ExperimentDashboard />
  </div>
</template>

<script>
import ExperimentDashboard from './components/ExperimentDashboard';

export default {
  name: 'AppDashboard',
  components: {
    ExperimentDashboard
  }
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}
</style>