<template>
  <a-row :gutter="8">
    <a-col :span="12">
      <div class="frame">
        <ControlPanel :msg="'Control Panel'"></ControlPanel>
      </div>
    </a-col>
    <a-col :span="12">
      <div class="frame">
        <CorrelationMatrixView></CorrelationMatrixView>
      </div>
    </a-col>
  </a-row>
</template>

<script>
import ControlPanel from '@/components/ControlPanel.vue'
import CorrelationMatrixView from "@/components/CorrelationMatrixView";

export default {
  name: 'App',
  components: {
    CorrelationMatrixView,
    ControlPanel
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  width: 1600px;
  height: 900px;
  margin: 10px;
  border: 2px solid lightblue;
}

.frame {
  border: 1px solid steelblue;
  padding: 5px 0;
}
</style>
