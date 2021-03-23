<template>
  <div id="pinus_layout_container">
    <a-row>
      <a-col :span="2">
        <a-row class="pinus_view_container">
          <PinusView
            :id="'market'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleMarket"
            :loading-triangle="loadingTriangleMarket"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'sector'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleSector"
            :loading-triangle="loadingTriangleSector"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'temp1'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleSector"
            :loading-triangle="loadingTriangleSector"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'temp2'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleSector"
            :loading-triangle="loadingTriangleSector"
          ></PinusView>
        </a-row>
        <a-row class="pinus_view_container">
          <PinusView
            :id="'temp3'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleSector"
            :loading-triangle="loadingTriangleSector"
          ></PinusView>
        </a-row>
      </a-col>
      <a-col :span="4">
        <a-row v-if="!isSwitch" id="pinus_view_switch_one">
          <PinusView
            :id="'big_market'"
            :period-range="periodRange"
            :correlation-triangle="correlationTriangleMarket"
            :loading-triangle="loadingTriangleMarket"
          ></PinusView>
        </a-row>
        <div v-if="isSwitch" >
          <a-row class="pinus_view_switch_three">
            <PinusView
              :id="'big_market1'"
              :period-range="periodRange"
              :correlation-triangle="correlationTriangleMarket"
              :loading-triangle="loadingTriangleMarket"
            ></PinusView>
          </a-row>
          <a-row class="pinus_view_switch_three">
            <PinusView
              :id="'big_market2'"
              :period-range="periodRange"
              :correlation-triangle="correlationTriangleMarket"
              :loading-triangle="loadingTriangleMarket"
            ></PinusView>
          </a-row>
          <!-- <a-row class="pinus_view_switch_three">
            <PinusView
              :id="'big_market3'"
              :period-range="periodRange"
              :correlation-triangle="correlationTriangleMarket"
              :loading-triangle="loadingTriangleMarket"
            ></PinusView>
          </a-row> -->
        </div>
      </a-col>
      <a-col :span="18">LineChart</a-col>
    </a-row>
  </div>
</template>

<script>
import PinusView from "@/components/PinusView/PinusView";
export default {
  name: "PinusLayout",
  components: {
    PinusView,
  },
  props: {
    periodRange: Array,
    correlationTriangleMarket: Object,
    correlationTriangleSector: Object,
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
#pinus_view_switch_one {
  height: 520px;
  border: 1px solid red;
  width: 100%;
}
.pinus_view_switch_three{
width: 100%;
height: 260px;
 border: 1px solid red;
}
</style>