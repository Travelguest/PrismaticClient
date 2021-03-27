<template>
  <div>
    <div>
      <a-row :gutter="[2, 2]">
        <a-col :span="6">
          <div id="control_panel_container">
            <ControlPanel
              @get-correlation-matrix="getCorrelationMatrixByYear"
            ></ControlPanel>
          </div>
        </a-col>
        <a-col :span="18">
          <a-row id="matrix_knowledge_graph_container" :gutter="2">
            <a-col :span="12">
              <div id="correlation_matrix_view_container">
                <CorrelationMatrixView
                  :selected-year="selectedYear"
                  :correlation-matrix="correlationMatrix"
                  :correlation-return="correlationReturn"
                  @selected-stock-from-matrix="updateSelectedStock"
                  @update-period-range="updatePeriodRange"
                >
                </CorrelationMatrixView>
              </div>
            </a-col>
            <a-col :span="12">
              <div id="knowledge_graph_container">
                <KnowledgeGraphView>
                  :stock-code="selectedStockLeft"
                  :knowledge-graph-count="knowledgeGraphCount"
                </KnowledgeGraphView>
              </div>
            </a-col>
          </a-row>

          <a-row id="detail_time_series_container">
            <PinusLayout
              :period-range="periodRange"
              :correlation-triangle-stock="correlationTriangleStock"
              :correlation-triangle-market-left="correlationTriangleMarketLeft"
              :correlation-triangle-market-right="
                correlationTriangleMarketRight
              "
              :correlation-triangle-sector-left="correlationTriangleSectorLeft"
              :correlation-triangle-sector-right="
                correlationTriangleSectorRight
              "
              :stock-a="selectedStockLeft"
              :stock-b="selectedStockRight"
              :loading-triangle-stock="loadingTriangleStock"
              :loading-triangle-market-left="loadingTriangleMarketLeft"
              :loading-triangle-market-right="loadingTriangleMarketRight"
              :loading-triangle-sector-left="loadingTriangleSectorLeft"
              :loading-triangle-sector-right="loadingTriangleSectorRight"
            />
          </a-row>
        </a-col>
      </a-row>
    </div>
    <!-- 测试用的container，之后删除 -->
    <!-- <div id="temp_container">
      <View></View>
    </div> -->
  </div>
</template>

<script>
import ControlPanel from "@/components/DynamicGraphView/ControlPanel";
import CorrelationMatrixView from "@/components/CorrelationMatrixView";
import PinusLayout from "@/components/PinusView/PinusLayout";
import KnowledgeGraphView from "@/components/KnowledgeGraphView";
// import View from "@/components/View";

import _ from "lodash";
import moment from "moment";
import "moment/dist/locale/zh-cn";
import DataService from "@/utils/data-service";

import matrix from "./components/data/matrix.json";
import stock_return from "./components/data/stock_return.json";
import pinus_stock from "./components/data/pinus_stock.json";
import pinus_market_left from "./components/data/pinus_market_left.json";
import pinus_market_right from "./components/data/pinus_market_right.json";
import pinus_sector_left from "./components/data/pinus_sector_left.json";
import pinus_sector_right from "./components/data/pinus_sector_right.json";
import knowledge_count from "./components/data/knowledge_count.json";

export default {
  name: "App",
  components: {
    ControlPanel,
    CorrelationMatrixView,
    PinusLayout,
    KnowledgeGraphView,
    // View,
  },
  computed: {},
  data() {
    return {
      periodRange: [
        moment.utc("2020-01-01", "YYYY-MM-DD"),
        moment.utc("2020-06-30", "YYYY-MM-DD"),
      ],
      selectedYear: null,
      selectedStockLeft: "000652",
      selectedStockRight: "000538",

      correlationMatrix: matrix,
      correlationReturn: stock_return,

      correlationTriangleStock: pinus_stock,
      correlationTriangleMarketLeft: pinus_market_left,
      correlationTriangleMarketRight: pinus_market_right,
      correlationTriangleSectorLeft: pinus_sector_left,
      correlationTriangleSectorRight: pinus_sector_right,

      loadingTriangleMarketLeft: false,
      loadingTriangleSectorLeft: false,
      loadingTriangleStock: false,
      loadingTriangleSectorRight: false,
      loadingTriangleMarketRight: false,

      numberOfSelectedPinus: 0,

      knowledgeGraphCount: knowledge_count,
    };
  },
  watch: {},
  mounted: function () {},
  methods: {
    updatePeriodRange(range) {
      this.periodRange = range;
      this.getCorrelationMatrix();
      this.getMatrixStockReturn();
    },
    updateSelectedStock(stock_left, stock_right) {
      this.selectedStockLeft = stock_left;
      this.selectedStockRight = stock_right;
      this.getCorrelationTriangle();
      this.getKnowledgeCount();
    },
    getCorrelationMatrixByYear(stock_list, year) {
      this.selectedYear = year;
      this.correlationMatrix.columns = stock_list;
    },
    getCorrelationMatrix() {
      DataService.post(
        "get_correlation_matrix",
        [
          this.correlationMatrix.columns,
          this.periodRange[0].format("YYYY-MM-DD"),
          this.periodRange[1].format("YYYY-MM-DD"),
        ],
        (data) => {
          this.correlationMatrix = data ? data : [];
        }
      );
    },
    getMatrixStockReturn() {
      DataService.post(
        "get_stock_return",
        [
          this.correlationMatrix.columns,
          this.periodRange[0].format("YYYY-MM-DD"),
          this.periodRange[1].format("YYYY-MM-DD"),
        ],
        (data) => {
          this.correlationReturn = data ? data : [];
        }
      );
    },
    getCorrelationTriangle() {
      this.loadingTriangleStock = true;
      DataService.post(
        "get_corr_tri_stock",
        _.flatten([
          this.selectedStockLeft,
          this.selectedStockRight,
          this.periodRange[0].format("YYYY-MM-DD"),
          this.periodRange[1].format("YYYY-MM-DD"),
        ]),
        (data) => {
          this.correlationTriangleStock = data;
          this.loadingTriangleStock = false;
        }
      );

      this.loadingTriangleMarketLeft = true;
      DataService.post(
        "get_corr_tri_market",
        _.flatten([
          this.selectedStockLeft,
          this.periodRange[0].format("YYYY-MM-DD"),
          this.periodRange[1].format("YYYY-MM-DD"),
        ]),
        (data) => {
          this.correlationTriangleMarketLeft = data;
          this.loadingTriangleMarketLeft = false;
        }
      );

      this.loadingTriangleMarketRight = true;
      DataService.post(
        "get_corr_tri_market",
        _.flatten([
          this.selectedStockRight,
          this.periodRange[0].format("YYYY-MM-DD"),
          this.periodRange[1].format("YYYY-MM-DD"),
        ]),
        (data) => {
          this.correlationTriangleMarketRight = data;
          this.loadingTriangleMarketRight = false;
        }
      );

      this.loadingTriangleSectorLeft = true;
      DataService.post(
        "get_corr_tri_sector",
        _.flatten([
          this.selectedStockLeft,
          this.periodRange[0].format("YYYY-MM-DD"),
          this.periodRange[1].format("YYYY-MM-DD"),
        ]),
        (data) => {
          this.correlationTriangleSectorLeft = data;
          this.loadingTriangleSectorLeft = false;
        }
      );

      this.loadingTriangleStock = true;
      DataService.post(
        "get_corr_tri_sector",
        _.flatten([
          this.selectedStockRight,
          this.periodRange[0].format("YYYY-MM-DD"),
          this.periodRange[1].format("YYYY-MM-DD"),
        ]),
        (data) => {
          this.correlationTriangleSectorRight = data;
          this.loadingTriangleSectorRight = false;
        }
      );
    },
    getKnowledgeCount() {
      DataService.post(
        "get_knowledge_graph_count",
        [this.selectedStockLeft],
        (data) => {
          this.knowledgeGraphCount = data;
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
#temp_container {
  height: 300px;
  width: 100%;
  border: 1px solid red;
}
</style>
