<template>
  <a-row :gutter="[5, 10]">
    <a-col :span="6">
      <div class="upper_row">
        <ControlPanel
            @get-correlation-matrix="getCorrelationMatrix"
        ></ControlPanel>
      </div>
    </a-col>
    <a-col :span="9">
      <div class="upper_row">
        <CorrelationMatrixView
            :correlation-matrix="correlationMatrix"
        ></CorrelationMatrixView>
      </div>
    </a-col>
    <a-col :span="9">
      <div class="upper_row">
        <View></View>
      </div>
    </a-col>
  </a-row>
  <a-row :gutter="[5, 10]">
    <a-col :span="18">
      <div class="lower_row">
        <View></View>
      </div>
    </a-col>
    <a-col :span="6">
      <div class="lower_row">
        <View></View>
      </div>
    </a-col>
  </a-row>
</template>

<script>
import ControlPanel from '@/components/ControlPanel.vue';
import CorrelationMatrixView from "@/components/CorrelationMatrixView";
import View from "@/components/View";

import DataService from "@/utils/data-service";

import matrix from './components/matrix.json'

export default {
  name: 'App',
  components: {
    CorrelationMatrixView,
    ControlPanel,
    View
  },
  data() {
    return {
      correlationMatrix: matrix,
    }
  },
  mounted: function () {
  },
  methods: {
    getCorrelationMatrix() {
      DataService.get('get_correlation_matrix', (data) => {
        this.correlationMatrix = data;
      });
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  width: 2000px;
  height: 1125px;
  margin: 2px;
  border: 2px solid lightblue;
}

.upper_row {
  border: 1px solid steelblue;
  width: 100%;
  height: 600px;
}

.lower_row {
  border: 1px solid steelblue;
  width: 100%;
  height: 515px;
}
</style>
