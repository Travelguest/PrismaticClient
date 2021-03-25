<template>
  <div style="height: 100%">
    <a-divider>Selected stocks and correlation threshold</a-divider>
    <a-row type="flex" class="panel">
      <a-select
          style="width: 100%; font-size: 12px"
          v-model:value="stockSelected"
          mode="multiple"
          allowClear
          placeholder="Search by stocks"
          option-label-prop="label"
      >
        <a-select-option
            disabled
            style="color: steelblue; font-size: 14px"
        >
          <p style="text-align: left; width:20%; display: inline-block"> <b>Code</b> </p>
          <p style="text-align: left; width:25%;  display: inline-block;"> <b>Company</b></p>
          <p style="text-align: center; width:25%;  display: inline-block"> <b>Sector</b> </p>
          <p style="text-align: center; width:30%;  display: inline-block"> <b>Subsector</b> </p>
        </a-select-option>
        <a-select-option
            v-for='stock in stockList'
            :key='stock.ts_code'
            :label="stock.ts_code"
            style="font-size: 12px"
        >
          <p style="text-align: left; width:20%; display: inline-block">{{ stock.ts_code }}</p>
          <p style="text-align: left; width:25%;  display: inline-block">{{ stock.name }}</p>
          <p style="text-align: center; width:25%;  display: inline-block">{{ stock.level1 }}</p>
          <p style="text-align: center; width:30%;  display: inline-block">{{ stock.level3 }}</p>
        </a-select-option>
      </a-select>
    </a-row>
    <a-row>
      <a-col :span="22">
        <a-slider
            range
            :tooltipVisible="false"
            v-model:value="correlationRange"
            :min="-1"
            :max="1"
            :step="0.01"
            :marks="correlationMarks"
            @change="onCorrelationSliderChange"
        />
      </a-col>
      <a-col :span="2" align="middle">
        <a-button
            shape="circle"
            type="primary"
            :loading="correlationButtonLoading"
            :disabled="stockButtonDisabled"
            @click="onCorrelationButtonClick"
        >
          <template #icon><FilterOutlined/></template>
        </a-button>
      </a-col>
    </a-row>

    <a-divider>Correlated clusters</a-divider>
    <dynamic-graph-view
        class="dynamic-graph"
        :corr-distribution="corrDistribution"
        :corr-cluster="corrCluster"
    >
    </dynamic-graph-view>

    <a-divider>Business tag filters</a-divider>
    <a-row justify="space-around" class="tag-cards">
      <a-tabs tabPosition="top" size="small">
        <a-tab-pane key="L1" tab="Industry">
          <a-tag color="purple" v-for="tag in businessTag.L1" :key="tag">
            {{ tag.name }}({{ tag.count}})
          </a-tag>
        </a-tab-pane>
        <a-tab-pane key="L2" tab="Sector">
          <a-tag color="blue" v-for="tag in businessTag.L2" :key="tag">
            {{ tag.name }}({{ tag.count}})
          </a-tag>
        </a-tab-pane>
        <a-tab-pane key="L3" tab="Subsector">
          <a-tag color="cyan" v-for="tag in businessTag.L3" :key="tag">
            {{ tag.name }}({{ tag.count}})
          </a-tag>
        </a-tab-pane>
        <a-tab-pane key="Concept" tab="Concept">
          <a-tag color="orange" v-for="tag in businessTag.concept" :key="tag">
            {{ tag.name }}({{ tag.count}})
          </a-tag>
        </a-tab-pane>
<!--        <template #tabBarExtraContent>-->
<!--          <a-button>Filter</a-button>-->
<!--        </template>-->
      </a-tabs>
    </a-row>
  </div>
</template>

<script>
import DataService from "@/utils/data-service";
import index_corr_dist from "@/components/data/index_corr_dist.json";
import corr_clusters_all_years from "@/components/data/corr_clusters_all_years.json"
import business_tag_table from "@/components/data/business_tag_table.json"
import DynamicGraphView from "@/components/DynamicGraphView/DynamicGraphView";
import {FilterOutlined} from '@ant-design/icons-vue';
export default {
  name: 'ControlPanel',
  components: {
    DynamicGraphView,
    FilterOutlined,
  },
  props: {
  },
  emits: [
    'get-correlation-matrix',
    'update-period-range'
  ],
  data() {
    return {
      stockList: [{ts_code:'000001.SH', name:'上证指数', level1:'index', level3:'composite'}],
      stockSelectionNumMax: 5,
      stockSelected: ['000652', '000538'],

      corrDistribution: index_corr_dist,

      correlationRange: [0.7, 1],
      correlationMarks: {0.6: '0.6', 0: '0', 1: '1'},
      correlationButtonLoading: false,

      corrCluster: corr_clusters_all_years,
      businessTag: business_tag_table,
    }
  },
  computed: {
    stockButtonDisabled() {
      return !this.stockSelected.length;
    },
  },
  watch: {
    periodRange: function() {
      this.$emit('update-period-range', this.periodRange);
    },
    stockSelected: function(_, newVal) {
      // Remove the last element if the selected number of stocks exceeds maximum
      if ( newVal.length >= this.stockSelectionNumMax ) {
        this.stockSelected.splice(this.stockSelectionNumMax,1);
      } else {
        // Whenever stocks are selected, update the correlation distribution
        DataService.post('get_corr_dist', this.stockSelected, data => {
          this.corrDistribution = data;
        })
      }
    }
  },
  mounted: function () {
    DataService.get('get_stock_list', data => {
      this.stockList = data;
    })
  },
  methods: {
    onCorrelationSliderChange(val) {
      this.correlationMarks = {0: '0'};
      this.correlationMarks[val[0]] = ''+val[0];
      this.correlationMarks[val[1]] = ''+val[1];
    },
    onCorrelationButtonClick() {
      this.correlationButtonLoading = !this.correlationButtonLoading;
      DataService.post('get_corr_clusters_all_years', this.correlationRange,(data) => {
        this.correlationButtonLoading = !this.correlationButtonLoading;
        this.corrCluster = data;
      });
      DataService.post('get_business_tag_table', this.correlationRange,(data) => {
        this.businessTag = data;
      });
    },
    onClusterButtonClick() {
      this.$emit('get-correlation-matrix');
    },
  }
}
</script>

<style scoped>

.panel {
  padding: 4px;
}
.dynamic-graph {
  height: 650px;
  overflow: auto;
}
.tag-cards {
  height: 200px;
  overflow: auto;
}
</style>
