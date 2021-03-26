<template>
  <div>
    <a-row :gutter="[2, 2]">
      <a-col :span="6">
        <div id="control_panel_container">
          <ControlPanel
            @get-correlation-matrix="getCorrelationMatrix"
            @update-period-range="updatePeriodRange"
          ></ControlPanel>
        </div>
      </a-col>
      <a-col :span="18">
        <a-row id="matrix_knowledge_graph_container" :gutter="2">
          <a-col :span="12">
            <div id="correlation_matrix_view_container">
              <CorrelationMatrixView
                :correlation-matrix="correlationMatrix"
                @selected-stock-from-matrix-diagonal="updateSelectedStockMarket"
                @selected-stock-from-matrix="updateSelectedStockAgainst"
              >
              </CorrelationMatrixView>
            </div>
          </a-col>
          <a-col :span="12">
            <div id="knowledge_graph_container">
              <View></View>
            </div>
          </a-col>
        </a-row>

        <a-row id="detail_time_series_container">
          <PinusLayout 
            :period-range="selectedRange"
            :correlation-triangle-stock="correlationTriangleStock"
            :correlation-triangle-market-left="correlationTriangleMarketLeft"
            :correlation-triangle-market-right="correlationTriangleMarketRight"
            :correlation-triangle-sector-left="correlationTriangleSectorLeft"
            :correlation-triangle-sector-right="correlationTriangleSectorRight"
            :stock-a="selectedStockLeft"
            :stock-b="selectedStockRight"
            :loading-triangle-market="loadingTriangleMarket"
            :loading-triangle-sector="loadingTriangleSector"
          />
        </a-row>

      </a-col>
    </a-row>

  </div>
</template>

<script>
import ControlPanel from "@/components/DynamicGraphView/ControlPanel";
import CorrelationMatrixView from "@/components/CorrelationMatrixView";
import PinusLayout from "@/components/PinusView/PinusLayout";
import View from "@/components/View";

import _ from "lodash";
import moment from "moment";
import DataService from "@/utils/data-service";

import matrix from "./components/data/matrix.json";
import pinus_stock from "./components/data/pinus_stock.json";
import pinus_market_left from "./components/data/pinus_market_left.json";
import pinus_market_right from "./components/data/pinus_market_right.json";
import pinus_sector_left from "./components/data/pinus_sector_left.json";
import pinus_sector_right from "./components/data/pinus_sector_right.json";

export default {
  name: "App",
  components: {
    PinusLayout,
    CorrelationMatrixView,
    ControlPanel,
    View,
  },
  computed: {
    selectedRange() {
      return this.periodRange === undefined || this.periodRange.length === 0
        ? [
            moment.utc("2020-01-01", "YYYY-MM-DD"),
            moment.utc("2020-06-30", "YYYY-MM-DD"),
          ]
        : this.periodRange;
    },
  },
  data() {
    return {
      periodRange: [],
      selectedStockLeft: "000652",
      selectedStockRight: "000538",

      correlationMatrix: matrix,
      correlationTriangleStock: pinus_stock,
      correlationTriangleMarketLeft: pinus_market_left,
      correlationTriangleMarketRight: pinus_market_right,
      correlationTriangleSectorLeft: pinus_sector_left,
      correlationTriangleSectorRight: pinus_sector_right,

      loadingTriangleMarket: false,
      loadingTriangleSector: false,

      numberOfSelectedPinus: 0,
    };
  },
  watch: {},
  mounted: function () {},
  methods: {
    handlePinusViewClick(event,d){
      console.log("被点击了：",event,d);
    },
    updatePeriodRange(range) {
      this.periodRange = range;
    },
    updateSelectedStockMarket(stock) {
      this.selectedStockLeft = stock;
      this.selectedStockRight = stock;
      this.getCorrelationTriangleMarket();
    },
    updateSelectedStockAgainst(stock_left, stock_right) {
      this.selectedStockLeft = stock_left;
      this.selectedStockRight = stock_right;
      this.getCorrelationTriangleStock();
    },
    getCorrelationMatrix(year, stock_list) {
      DataService.post("get_correlation_matrix", [year, stock_list], (data) => {
        this.correlationMatrix = data ? data : [];
      });
    },
    getCorrelationTriangleMarket() {
      this.loadingTriangleMarket = true;
      DataService.post(
        "get_corr_tri_market",
        _.flatten([this.selectedStockLeft, this.selectedRange]),
        (data) => {
          this.correlationTriangleMarketLeft = data;
          this.loadingTriangleMarket = false;
        }
      );
      DataService.post(
        "get_corr_tri_market",
        _.flatten([this.selectedStockRight, this.selectedRange]),
        (data) => {
          this.correlationTriangleMarketRight = data;
          this.loadingTriangleMarket = false;
        }
      );

      this.loadingTriangleSector = true;
      DataService.post(
        "get_corr_tri_sector",
        _.flatten([this.selectedStockLeft, this.selectedRange]),
        (data) => {
          this.correlationTriangleSectorLeft = data;
          this.loadingTriangleSector = false;
        }
      );

      this.loadingTriangleSector = true;
      DataService.post(
        "get_corr_tri_sector",
        _.flatten([this.selectedStockRight, this.selectedRange]),
        (data) => {
          this.correlationTriangleSectorRight = data;
          this.loadingTriangleSector = false;
        }
      );
    },
    getCorrelationTriangleStock() {
      this.loadingTriangleMarket = true;
      DataService.post(
        "get_corr_tri_market",
        _.flatten([this.selectedStockLeft, this.selectedRange]),
        (data) => {
          this.correlationTriangleMarketLeft = data;
          this.loadingTriangleMarket = false;
        }
      );

      this.loadingTriangleMarket = true;
      DataService.post(
        "get_corr_tri_market",
        _.flatten([this.selectedStockRight, this.selectedRange]),
        (data) => {
          this.correlationTriangleMarketRight = data;
          this.loadingTriangleMarket = false;
        }
      );

      this.loadingTriangleSector = true;
      DataService.post(
        "get_corr_tri_stock",
        _.flatten([
          this.selectedStockLeft,
          this.selectedStockRight,
          this.selectedRange,
        ]),
        (data) => {
          this.correlationTriangleStock = data;
          this.loadingTriangleSector = false;
        }
      );

      this.loadingTriangleSector = true;
      DataService.post(
        "get_corr_tri_sector",
        _.flatten([this.selectedStockLeft, this.selectedRange]),
        (data) => {
          this.correlationTriangleSectorLeft = data;
          this.loadingTriangleSector = false;
        }
      );

      this.loadingTriangleSector = true;
      DataService.post(
        "get_corr_tri_sector",
        _.flatten([this.selectedStockRight, this.selectedRange]),
        (data) => {
          this.correlationTriangleSectorRight = data;
          this.loadingTriangleSector = false;
        }
      );
    },
  },
};
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

/* .upper_row {
  border: 1px dotted steelblue;
  width: 100%;
  height: 600px;
}

.lower_row {
  border: 1px dotted steelblue;
  width: 100%;
  height: 520px;
} */

#control_panel_container {
  height: 1123px;
  border: 1px solid steelblue;
  width: 100%;
  box-sizing: border-box;
}
#matrix_knowledge_graph_container {
  box-sizing: border-box;
  height: 600px;
  width: 100%;
  margin-bottom: 2px;
}
#correlation_matrix_view_container {
  box-sizing: border-box;
  height: 600px;
  width: 100%;

  /* margin-right: 2px; */
  border: 1px solid steelblue;
}
#knowledge_graph_container {
  height: 600px;
  width: 100%;
  border: 1px solid steelblue;
}
#detail_time_series_container {
  height: 520px;
  width: 100%;
  border: 1px solid steelblue;
}
.pinus_view_container{
  height: 104px;
  width: 100%;
  /* border: 1px solid red; */
}
</style>
