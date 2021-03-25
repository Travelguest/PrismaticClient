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
              :id="showTopPinusID"
              :period-range="periodRange"
              :correlation-triangle="showTopPinusData"
              :loading-triangle="loadingTriangleMarket"
            ></PrismView>
          </a-row>
          <a-row class="pinus_view_switch_two">
            <PrismView
              :id="showBottomPinusID"
              :period-range="periodRange"
              :correlation-triangle="showBottomPinusData"
              :loading-triangle="loadingTriangleMarket"
            ></PrismView>
          </a-row>
        </div>
      </a-col>
      <a-col :span="17">LineChart</a-col>
    </a-row>
  </div>
</template>

<script>
import PinusView from "@/components/PinusView/PinusView";
import PrismView from "@/components/PinusView/PrismView";

export default {
  name: "PinusLayout",
  components: {
    PinusView,
    PrismView,
  },
  props: {
    periodRange: Array,
    //correlation-triangle的值
    correlationTriangleMarketLeft: Object,
    correlationTriangleMarketRight: Object,
    correlationTriangleStock: Object,
    correlationTriangleSectorLeft: Object,
    correlationTriangleSectorRight: Object,

    loadingTriangleMarket: Boolean,
    loadingTriangleSector: Boolean,
  },
  data() {
    return {
      showMap: {
        MarketLeft: false,
        SectorLeft: false,
        Stock: false,
        SectorRight: false,
        MarketRight: false,
      },
      showTopPinusData: this.correlationTriangleMarketLeft,
      showBottomPinusData: this.correlationTriangleMarketRight,
      showTopPinusID: "MarketLeftDetail",
      showBottomPinusID: "MarketRightDetail",
    };
  },
  computed: {},

  watch: {},
  mounted() {},
  methods: {
    handleClick(id) {
      this.showMap[id] = !this.showMap[id];
      console.log(id);
      //前两个画图
      let cnt = 0;
      for (let key in this.showMap) {
        if (this.showMap[key]) {
          cnt++;
          if (cnt === 1) {
            if (key === "MarketLeft") {
              this.showTopPinusData = this.correlationTriangleMarketLeft;
            //   this.showTopPinusID = "MarketLeft";
            } else if (key === "SectorLeft") {
              this.showTopPinusData = this.correlationTriangleSectorLeft;
            //   this.showTopPinusID = "SectorLeft";
            } else if (key === "Stock") {
              this.showTopPinusData = this.correlationTriangleStock;
            //   this.showTopPinusID = "Stock";
            } else if (key === "SectorRight") {
              this.showTopPinusData = this.correlationTriangleSectorRight;
            //   this.showTopPinusID = "SectorRight";
            } else {
              this.showTopPinusData = this.correlationTriangleMarketRight;
            //   this.showTopPinusID = "MarketRight";
            }
            this.showTopPinusID = key+"Detail";
          } else if (cnt === 2) {
            if (key === "MarketLeft") {
              this.showBottomPinusData = this.correlationTriangleMarketLeft;
             
            } else if (key === "SectorLeft") {
              this.showBottomPinusData = this.correlationTriangleSectorLeft;
            } else if (key === "Stock") {
              this.showBottomPinusData = this.correlationTriangleStock;
            } else if (key === "SectorRight") {
              this.showBottomPinusData = this.correlationTriangleSectorRight;
            } else {
              this.showBottomPinusData = this.correlationTriangleMarketRight;
            }
             this.showBottomPinusID = key + "Detail";
          }
        }
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
</style>