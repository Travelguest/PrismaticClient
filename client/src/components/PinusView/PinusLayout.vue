<template>
    <div id="pinus_layout_container">
      <div id="Prism_Time_Series_title"><div id="Prism_Time_Series_text">Prism Time Series</div></div>
    <div id="triangle"></div>
      <a-row>
        <a-col :span="2">
          <a-row class="pinus_view_container">
            <PinusView
              :id="'MarketLeft'"
              :period-range="periodRange"
              :correlation-triangle="correlationTriangleMarketLeft"
              :loading-triangle="loadingTriangleMarketLeft"
              @clickedPinus="handleClick"
            ></PinusView>
          </a-row>
          <a-row class="pinus_view_container">
            <PinusView
              :id="'SectorLeft'"
              :period-range="periodRange"
              :correlation-triangle="correlationTriangleSectorLeft"
              :loading-triangle="loadingTriangleSectorLeft"
              @clickedPinus="handleClick"
            ></PinusView>
          </a-row>
          <a-row class="pinus_view_container">
            <PinusView
              :id="'Stock'"
              :period-range="periodRange"
              :correlation-triangle="correlationTriangleStock"
              :loading-triangle="loadingTriangleStock"
              @clickedPinus="handleClick"
            ></PinusView>
          </a-row>
          <a-row class="pinus_view_container">
            <PinusView
              :id="'SectorRight'"
              :period-range="periodRange"
              :correlation-triangle="correlationTriangleSectorRight"
              :loading-triangle="loadingTriangleSectorRight"
              @clickedPinus="handleClick"
            ></PinusView>
          </a-row>
          <a-row class="pinus_view_container">
            <PinusView
              :id="'MarketRight'"
              :period-range="periodRange"
              :correlation-triangle="correlationTriangleMarketRight"
              :loading-triangle="loadingTriangleMarketRight"
              @clickedPinus="handleClick"
            ></PinusView>
          </a-row>
        </a-col>
        <a-col :span="5">
          <div>
            <a-row class="pinus_view_switch_two">
              <PrismView
                :id="'topDetail'"
                :title="showTopPinusTitle"
                :period-range="periodRange"
                :correlation-triangle="showTopPinusData"
                v-on:updateBrush="handleUpdateBrush"
              ></PrismView>
            </a-row>
            <a-row class="pinus_view_switch_two">
              <PrismView
                :id="'bottomDetail'"
                :title="showBottomPinusTitle"
                :period-range="periodRange"
                :correlation-triangle="showBottomPinusData"
                v-on:updateBrush="handleUpdateBrush"
              ></PrismView>
            </a-row>
          </div>
        </a-col>
        <a-col :span="17">
          <a-row style="height: 260px; width: 100%">
            <LineChart
              v-if="isShowTopLineChart"
              :id="'top'"
              :title="topLineChartTitle"
              :stock-a="stockA"
              :stock-b="stockB"
              :preprocessed-data="topLineChartData"
            >
            </LineChart>
          </a-row>
          <a-row style="height: 260px; width: 100%">
            <LineChart
              v-if="isShowBottomLineChart"
              :id="'bottom'"
              :title="bottomLineChartTitle"
              :stock-a="stockA"
              :stock-b="stockB"
              :preprocessed-data="bottomLineChartData"
            >
            </LineChart>
          </a-row>
        </a-col>
      </a-row>
    </div>
</template>

<script>
import PinusView from "@/components/PinusView/PinusView";
import PrismView from "@/components/PinusView/PrismView";
import LineChart from "@/components/PinusView/LineChart";
import DataService from "@/utils/data-service";

export default {
  name: "PinusLayout",
  components: {
    PinusView,
    PrismView,
    LineChart,
  },
  props: {
    periodRange: Array,
    //correlation-triangle的值
    correlationTriangleMarketLeft: Object,
    correlationTriangleMarketRight: Object,
    correlationTriangleStock: Object,
    correlationTriangleSectorLeft: Object,
    correlationTriangleSectorRight: Object,

    //股票A,B
    stockA: String,
    stockB: String,

    loadingTriangleMarketLeft: Boolean,
    loadingTriangleSectorLeft: Boolean,
    loadingTriangleStock: Boolean,
    loadingTriangleSectorRight: Boolean,
    loadingTriangleMarketRight: Boolean,
  },
  data() {
    return {
      // pinusDataMap: {
      //   MarketLeft: this.correlationTriangleMarketLeft,
      //   SectorLeft: this.correlationTriangleSectorLeft,
      //   Stock: this.correlationTriangleStock,
      //   SectorRight: this.correlationTriangleSectorRight,
      //   MarketRight: this.correlationTriangleMarketRight,
      // },
      showMap: {
        top: "",
        bottom: "",
      },
      //传给Prism的信息
      showTopPinusData: null,
      showBottomPinusData: null,
      showTopPinusTitle: "",
      showBottomPinusTitle: "",
      start_date: "2010-02-01",
      end_date: "2020-04-30",
      stock_code: this.stockA,
      index_type: "",

      //传给LineChart的信息
      topLineChartTitle: "",
      bottomLineChartTitle: "",
      topLineChartData: null,
      bottomLineChartData: null,
      isShowTopLineChart: false,
      isShowBottomLineChart: false,
    };
  },
  computed: {},

  watch: {
    correlationTriangleMarketLeft: function () {
      this.showTopPinusData = null;
      this.showBottomPinusData = null;
      this.showTopPinusTitle = "";
      this.showBottomPinusTitle = "";
      this.showMap.top = "";
      this.showMap.bottom = "";
      this.isShowTopLineChart = false;
      this.isShowBottomLineChart = false;
    },
  },
  mounted() {},
  methods: {
    pinusDataMap: function (id) {
      if (id === "MarketLeft") return this.correlationTriangleMarketLeft;
      else if (id === "SectorLeft") return this.correlationTriangleSectorLeft;
      else if (id === "Stock") return this.correlationTriangleStock;
      else if (id === "SectorRight") return this.correlationTriangleSectorRight;
      else if (id === "MarketRight") return this.correlationTriangleMarketRight;
      else return null;
    },
    handleClick(id) {
      if (!this.showMap.top) {
        this.showMap.top = id;
        this.showTopPinusData = this.pinusDataMap(id);
        this.showTopPinusTitle = id;
      } else if (id === this.showMap.top) {
        this.showTopPinusData = null;
        this.showMap.top = "";
        this.showTopPinusTitle = "";
        this.isShowTopLineChart = false;
      } else if (!this.showMap.bottom) {
        this.showMap.bottom = id;
        this.showBottomPinusData = this.pinusDataMap(id);
        this.showBottomPinusTitle = id;
      } else if (id === this.showMap.bottom) {
        this.showBottomPinusData = null;
        this.showMap.bottom = "";
        this.showBottomPinusTitle = "";
        this.isShowBottomLineChart = false;
      }
    },
    handleUpdateBrush(start, end, title) {
      this.start_date = start;
      this.end_date = end;
      // console.log(
      //   "得到start,end:",
      //   start,
      //   end,
      //   title,
      //   this.stockA,
      //   this.stockB
      // );
      if (title === "Stock") {
        // can only get AB
        DataService.post(
          "get_stock_daily",
          [[this.stockA, this.stockB], this.start_date, this.end_date],
          (data) => {
            // this.businessTag = data;
            // console.log("Stock得到的数据：", data);
            if (title === this.showTopPinusTitle) {
              //如果是top触发的Brush
              // console.log("Stock在Top");
              this.topLineChartData = data;
              this.topLineChartTitle = title;
              this.isShowTopLineChart = true;
            } else if (title === this.showBottomPinusTitle) {
              //bottom触发的Brush
              // console.log("Stock在Bottom");
              this.bottomLineChartData = data;
              this.bottomLineChartTitle = title;
              this.isShowBottomLineChart = true;
            }
          }
        );
      } else {
        if (title === "MarketLeft" || title === "SectorLeft") {
          this.stock_code = this.stockA;
        } else if (title === "MarketRight" || title === "SectorRight") {
          this.stock_code = this.stockB;
        }
        if (title === "SectorLeft" || title === "SectorRight") {
          this.index_type = "industry";
        } else {
          this.index_type = "market";
        }
        // console.log(
        //   "不是Stock,传入：",
        //   this.stock_code,
        //   this.index_type,
        //   this.start_date,
        //   this.end_date
        // );
        // can get AM, AI, BI, BM
        DataService.post(
          "get_stock_index_daily",
          [this.stock_code, this.index_type, this.start_date, this.end_date],
          (data) => {
            // console.log(`其余的${title}得到的数据：`, data);
            if (title === this.showTopPinusTitle) {
              // console.log(`${title}在Top`);
              this.topLineChartData = data;
              this.topLineChartTitle = title;
              this.isShowTopLineChart = true;
            } else if (title === this.showBottomPinusTitle) {
              // console.log(`${title}在Bottom`);
              this.bottomLineChartData = data;
              this.bottomLineChartTitle = title;
              this.isShowBottomLineChart = true;
            }
          }
        );
      }
    },
  },
};
</script>


<style scoped>
#pinus_layout_container {
  width: 100%;
  height: 100%;
}
.pinus_view_container {
  height: 104px;
  width: 100%;
  /* border: 1px solid red; */
}
.pinus_view_switch_two {
  width: 100%;
  height: 260px;
}
#Prism_Time_Series_title {
  position: absolute;
  right: 0;
  top: 50;
  padding: 0 20px;
  width: 309.531px;
  height: 40px;
  line-height: 40px;
  font-size: 24px;
  background: #777;
  color: #fcfcfc;
  display: flex;
  font-weight: bold;
  border-radius: 2px;
  box-shadow: 0 1px 2px rgba(26 26 26 0.2);
}
#Prism_Time_Series_text {
  position: absolute;
  right: 0;
  padding-right: 20px;
  text-align: right;
}

#triangle {
  position: absolute;
  top: 50;
  right: 309.531px;
  border-top: 40px solid #777;
  border-left: 45px solid #ffffff;
  border-bottom: 3px solid #ffff;
}
</style>