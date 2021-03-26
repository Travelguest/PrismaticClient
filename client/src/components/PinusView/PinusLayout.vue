<template>
  <div id="pinus_layout_container">
    <a-row>
      <a-col :span="2">
        <a-row class="pinus_view_container">
          <PinusView
            :id="'MarketLeft'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleMarketLeft"
            :loading-triangle="loadingTriangleMarket"
            @clickedPinus="handleClick"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'SectorLeft'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleSectorLeft"
            :loading-triangle="loadingTriangleSector"
            @clickedPinus="handleClick"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'Stock'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleStock"
            :loading-triangle="loadingTriangleSector"
            @clickedPinus="handleClick"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'SectorRight'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleSectorRight"
            :loading-triangle="loadingTriangleSector"
            @clickedPinus="handleClick"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'MarketRight'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleMarketRight"
            :loading-triangle="loadingTriangleMarket"
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
              :loading-triangle="loadingTriangleMarket"
              v-on:updateBrush="handleUpdateBrush"
            ></PrismView>
          </a-row>
          <a-row class="pinus_view_switch_two">
            <PrismView
              :id="'bottomDetail'"
              :title="showBottomPinusTitle"
              :period-range="periodRange"
              :correlation-triangle="showBottomPinusData"
              :loading-triangle="loadingTriangleMarket"
              v-on:updateBrush="handleUpdateBrush"
            ></PrismView>
          </a-row>
        </div>
      </a-col>
      <a-col :span="17">
        <a-row>
          <LineChart> </LineChart>
        </a-row>
        <a-row>
          <LineChart> </LineChart>
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

    loadingTriangleMarket: Boolean,
    loadingTriangleSector: Boolean,
  },
  data() {
    return {
      pinusDataMap: {
        MarketLeft: this.correlationTriangleMarketLeft,
        SectorLeft: this.correlationTriangleSectorLeft,
        Stock: this.correlationTriangleStock,
        SectorRight: this.correlationTriangleSectorRight,
        MarketRight: this.correlationTriangleMarketRight,
      },
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
      stock_code:this.stockA,
      index_type:'',
    };
  },
  computed: {},

  watch: {},
  mounted() {},
  methods: {
    handleClick(id) {
      if (!this.showMap.top) {
        this.showMap.top = id;
        this.showTopPinusData = this.pinusDataMap[id];
        this.showTopPinusTitle = id;
      } else if (id === this.showMap.top) {
        this.showTopPinusData = null;
        this.showMap.top = "";
        this.showTopPinusTitle = "";
      } else if (!this.showMap.bottom) {
        this.showMap.bottom = id;
        this.showBottomPinusData = this.pinusDataMap[id];
        this.showBottomPinusTitle = id;
      } else if (id === this.showMap.bottom) {
        this.showBottomPinusData = null;
        this.showMap.bottom = "";
        this.showBottomPinusTitle = "";
      }
    },
    handleUpdateBrush(start, end, title) {
      this.start_date = start;
      this.end_date = end;
      console.log("得到start,end:", start, end,title,this.stockA,this.stockB);
      if (title === "Stock") {
        // can only get AB
        DataService.post(
          "get_stock_daily",
          [[this.stockA,this.stockB], this.start_date, this.end_date],
          (data) => {
            // this.businessTag = data;
            console.log("Stock得到的数据：", data);
          }
        );
      } else {
        console.log("不是Stock")
        if(title === "MarketLeft" || title === "SectorLeft") {
          this.stock_code = this.stockA;
        }
        else if(title === "MarketRight" || title === "SectorRight") {
           this.stock_code = this.stockB;
        }
        if(title === "SectorLeft" || title === "SectorRight") {
          this.index_type = "industry";
        }
        else {
          this.index_type = "market";
        }
        console.log("传入：",this.stock_code, this.index_type, this.start_date, this.end_date);
        // can get AM, AI, BI, BM
        DataService.post(
          "get_stock_index_daily",
          [this.stock_code, this.index_type, this.start_date, this.end_date],
          (data) => {
            // this.businessTag = data;
            console.log("其余的得到的数据：",data);
          }
        );
      }
    },
    handleBrush() {
      // can only get AB
      DataService.post(
        "get_stock_daily",
        [
          [this.stock_code_left, this.stock_code_right],
          this.start_date,
          this.end_date,
        ],
        (data) => {
          // this.businessTag = data;
          console.log(data);
        }
      );

      // can get AM, AI, BI, BM
      DataService.post(
        "get_stock_index_daily",
        [this.stock_code, this.index_type, this.start_date, this.end_date],
        (data) => {
          // this.businessTag = data;
          console.log(data);
        }
      );
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
</style>