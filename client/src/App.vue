<template>
  <a-row :gutter="[5, 5]">
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
            @selected-stock-from-matrix-diagonal="updateSelectedStockMarket"
            @selected-stock-from-matrix="updateSelectedStockAgainst"
        ></CorrelationMatrixView>
      </div>
    </a-col>
    <a-col :span="5">
      <div class="upper_row">
        <PinusView
            :id="'market'"
            :period-range="selectedRange"
            :correlation-triangle="correlationTriangleMarket"
            :loading-triangle="loadingTriangleMarket"
        ></PinusView>
      </div>
    </a-col>
    <a-col :span="4">
      <div class="upper_row">
        <PinusView
            :id="'sector'"
            :period-range="selectedRange"
            :correlation-triangle="correlationTriangleSector"
            :loading-triangle="loadingTriangleSector"
        ></PinusView>
      </div>
    </a-col>
  </a-row>
  <a-row :gutter="[5, 5]">
    <a-col :span="5">
      <div class="lower_row">
        <View></View>
      </div>
    </a-col>
    <a-col :span="19">
      <div class="lower_row">
        <View></View>
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
import pinus_market from './components/pinus_market.json'
import pinus_sector from './components/pinus_sector.json'

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
      selectedStockAgainst: '000538',

      correlationMatrix: matrix,
      correlationTriangleMarket: pinus_market,
      correlationTriangleSector: pinus_sector,

      loadingTriangleMarket: false,
      loadingTriangleSector: false,
    }
  },
  watch: {
  },
  mounted: function () {
  },
  methods: {
    updatePeriodRange(range) {
      this.periodRange = range;
    },
    updateSelectedStockMarket(stock) {
      this.selectedStock = stock;
      this.getCorrelationTriangleMarket();
    },
    updateSelectedStockAgainst(stock_left, stock_right) {
      this.selectedStock = stock_left;
      this.selectedStockAgainst = stock_right;
      this.getCorrelationTriangleStock();
    },
    getCorrelationMatrix() {
      DataService.get('get_correlation_matrix', (data) => {
        this.correlationMatrix = data? data: [];
      });
    },
    getCorrelationTriangleMarket() {
      this.loadingTriangleMarket = true;
      DataService.post('get_corr_tri_market',
          _.flatten([this.selectedStock, this.selectedRange]),
          (data) => {
            this.correlationTriangleMarket = data;
            this.loadingTriangleMarket = false;
          });

      this.loadingTriangleSector = true;
      DataService.post('get_corr_tri_sector',
          _.flatten([this.selectedStock, this.selectedRange]),
          (data) => {
            this.correlationTriangleSector = data;
            this.loadingTriangleSector = false;
          });
    },
    getCorrelationTriangleStock() {
      this.loadingTriangleMarket = true;
      DataService.post('get_corr_tri_market',
          _.flatten([this.selectedStock, this.selectedRange]),
          (data) => {
            this.correlationTriangleMarket = data;
            this.loadingTriangleMarket = false;
          });

      this.loadingTriangleSector = true;
      DataService.post('get_corr_tri_stock',
          _.flatten([this.selectedStock, this.selectedStockAgainst, this.selectedRange]),
          (data) => {
            this.correlationTriangleSector = data;
            this.loadingTriangleSector = false;
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
  border: 1px solid lightblue;
}

.upper_row {
  border: 1px dotted steelblue;
  width: 100%;
  height: 600px;
}

.lower_row {
  border: 1px dotted steelblue;
  width: 100%;
  height: 520px;
}
</style>
