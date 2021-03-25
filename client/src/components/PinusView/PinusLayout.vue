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
            ></PrismView>
          </a-row>
          <a-row class="pinus_view_switch_two">
            <PrismView
              :id="'bottomDetail'"
              :title="showBottomPinusTitle"
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
      //   showTopPinusData: this.correlationTriangleMarketLeft,
      //   showBottomPinusData: this.correlationTriangleMarketRight,
      showTopPinusData: null,
      showBottomPinusData: null,
      showTopPinusTitle: "",
      showBottomPinusTitle: "",
    };
  },
  computed: {},

  watch: {},
  mounted() {},
  methods: {
    handleClick(id) {
      console.log(id);
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
      //   this.showMap[id] = !this.showMap[id];
      //   for (let key in this.showMap) {
      //     if (this.showMap[key]) {
      //       if (key === "MarketLeft") {
      //         this.showTopPinusData = this.correlationTriangleMarketLeft;
      //         this.showTopPinusTitle = key;
      //       } else if (key === "SectorLeft") {
      //         this.showTopPinusData = this.correlationTriangleSectorLeft;
      //         this.showTopPinusTitle = key;
      //       }
      //       if (key === "Stock") {
      //         this.showBottomPinusData = this.correlationTriangleStock;
      //         this.showBottomPinusTitle = key;
      //       } else if (key === "SectorRight") {
      //         this.showBottomPinusData = this.correlationTriangleSectorRight;
      //         this.showBottomPinusTitle = key;
      //       } else {
      //         this.showBottomPinusData = this.correlationTriangleMarketRight;
      //         this.showBottomPinusTitle = key;
      //       }
      //     }
      //   }
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