<template>
  <div id="vue">
    <!--    <a-row type="flex" justify="space-around" class="second-row" style="padding: 0px">-->
    <!--      <a-col :span="21" class="second-row">-->
    <!--        <a-range-picker-->
    <!--            style="width: 100%"-->
    <!--            v-model:value="periodRange"-->
    <!--            :disabledDate="periodDisabledRange"-->
    <!--            :ranges="periodPresetRange"-->
    <!--        />-->
    <!--      </a-col>-->
    <!--      <a-col :span="2" class="second-row">-->
    <!--        <a-button-->
    <!--            shape="circle"-->
    <!--            type="primary"-->
    <!--            :loading="periodButtonLoading"-->
    <!--            :disabled="periodButtonDisabled"-->
    <!--            @click="onPeriodButtonClick"-->
    <!--        >-->
    <!--          <template #icon><CalendarOutlined/></template>-->
    <!--        </a-button>-->
    <!--      </a-col>-->
    <!--    </a-row>-->
    <div id="knowledge_graph_title">Knowledge Graph</div>
    <div id="triangle"></div>
  </div>
</template>

<script>
import moment from "moment";
import 'moment/dist/locale/zh-cn';

export default {
  name: "View",
  data() {
    return {
      periodRange: [moment.utc('2020-01-01', 'YYYY-MM-DD'), moment.utc('2020-06-30', 'YYYY-MM-DD')],
      periodPresetRange: {
        'All': [moment.utc('2011-01-01', 'YYYY-MM-DD'), moment.utc('2020-12-31', 'YYYY-MM-DD')],
        '3Y': [moment.utc('2018-01-01', 'YYYY-MM-DD'), moment.utc('2020-12-31', 'YYYY-MM-DD')],
        '1Y': [moment.utc('2020-01-01', 'YYYY-MM-DD'), moment.utc('2020-12-31', 'YYYY-MM-DD')],
        '3M': [moment.utc('2020-01-01', 'YYYY-MM-DD'), moment.utc('2020-03-31', 'YYYY-MM-DD')],
      },
      periodDisabledRange: (cur) => { return cur < moment.utc('2011-01-01', 'YYYY-MM-DD') || cur > moment.utc('2020-12-31', 'YYYY-MM-DD')},
      periodButtonLoading: false,
    }
  },
}
</script>

<style scoped>
#knowledge_graph_title {
  background-color: #777;
  display: block;
  position: relative;
  padding: 0 20px;
  width: 50%;
  height: 40px;
  line-height: 40px;
  font-size: 26px;
  background: #777;
  color: #fcfcfc;

  display: flex;
  top: 0px;
  font-weight: bold;
  border-radius: 2px;
  box-shadow: 0 1px 2px rgb(26 26 26 / 20%);
}

#triangle {
  position: absolute;
  top: 0px;
  right: 350px;
  border-top: 40px solid #777;
  border-right: 45px solid #ffffff;
  border-bottom: 3px solid #ffff;
}
</style>