<template>
  <a-row :gutter="[5, 10]">
    <a-col :span="6">
      <div class="upper_row">
        <ControlPanel
            @get-correlation-matrix="getCorrelationMatrix"
            @update-period-range="updatePeriodRange"
        ></ControlPanel>
      </div>
    </a-col>
    <a-col :span="9">
      <div class="upper_row">
        <CorrelationMatrixView
            :correlation-matrix="correlationMatrix"
            @selected-stock-from-matrix="updateSelectedStock"
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
        <PinusView
            :selected-stock="selectedStock"
            :period-range="selectedRange"
            :correlation-triangle="correlationTriangle"
            :loading-triangle="loadingTriangle"
        ></PinusView>
      </div>
    </a-col>
  </a-row>
</template>

<script>
import ControlPanel from '@/components/ControlPanel.vue';
import CorrelationMatrixView from "@/components/CorrelationMatrixView";
import PinusView from "@/components/PinusView";
import View from "@/components/View";

import _ from 'lodash';
import moment from "moment";
import DataService from "@/utils/data-service";

import matrix from './components/matrix.json'
import pinus from './components/pinus.json'

export default {
  name: 'App',
  components: {
    PinusView,
    CorrelationMatrixView,
    ControlPanel,
    View
  },
  computed: {
    selectedRange() {
      return this.periodRange === undefined || this.periodRange.length === 0?
          [moment.utc('2020-01-01', 'YYYY-MM-DD'), moment.utc('2020-06-30', 'YYYY-MM-DD')]:
          this.periodRange
    }
  },
  data() {
    return {
      periodRange: [],
      selectedStock: '000652',

      correlationMatrix: matrix,
      correlationTriangle: pinus,

      loadingTriangle: false,
    }
  },
  watch: {
    selectedStock() {
      this.getCorrelationTriangle()
    },
  },
  mounted: function () {
  },
  methods: {
    updatePeriodRange(range) {
      this.periodRange = range;
    },
    updateSelectedStock(stock) {
      this.selectedStock = stock;
    },
    getCorrelationMatrix() {
      DataService.get('get_correlation_matrix', (data) => {
        this.correlationMatrix = data;
      });
    },
    getCorrelationTriangle() {
      this.loadingTriangle = true;
      DataService.post('get_corr_tri_market',
          _.flatten([this.selectedStock, this.selectedRange]),
          (data) => {
        this.correlationTriangle = data;
        this.loadingTriangle = false;
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
