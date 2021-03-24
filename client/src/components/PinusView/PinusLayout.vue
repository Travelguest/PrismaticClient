<template>
  <div id="pinus_layout_container">
    <a-row>
      <a-col :span="2">
        <a-row class="pinus_view_container">
          <PinusView
            :id="'market'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleMarketLeft"
            :loading-triangle="loadingTriangleMarket"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'sector'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleSectorLeft"
            :loading-triangle="loadingTriangleSector"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'temp1'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleStock"
            :loading-triangle="loadingTriangleSector"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'temp2'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleSectorRight"
            :loading-triangle="loadingTriangleSector"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'temp3'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleMarketRight"
            :loading-triangle="loadingTriangleMarket"
          ></PinusView>
        </a-row>
      </a-col>
      <a-col :span="4">
        <div>
          <a-row class="pinus_view_switch_two">
            <PrismView
              :id="'big_market1'"
              :period-range="periodRange"
              :correlation-triangle="correlationTriangleMarketLeft"
              :loading-triangle="loadingTriangleMarket"
            ></PrismView>
          </a-row>
          <a-row class="pinus_view_switch_two">
            <PrismView
              :id="'big_market2'"
              :period-range="periodRange"
              :correlation-triangle="correlationTriangleMarketRight"
              :loading-triangle="loadingTriangleMarket"
            ></PrismView>
          </a-row>
        </div>
      </a-col>
      <a-col :span="18">LineChart</a-col>
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
    correlationTriangleStock: Object,
    correlationTriangleMarketLeft: Object,
    correlationTriangleMarketRight: Object,
    correlationTriangleSectorLeft: Object,
    correlationTriangleSectorRight: Object,
    loadingTriangleMarket: Boolean,
    loadingTriangleSector: Boolean,
  },
  data() {
    return {
      isSwitch: true,
    };
  },
  computed: {},

  watch: {},
  mounted() {},
  methods: {},
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
  /* border: 1px solid red; */
}
</style>