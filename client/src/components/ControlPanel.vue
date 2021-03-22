<template>
  <div>
    <a-divider>Selected Stocks</a-divider>
    <a-row type="flex" justify="space-around" class="first-row" style="padding: 0px">
      <a-col :span="21" class="first-row">
        <a-select
            style="width: 100%; font-size: 13px"
            v-model:value="stockSelected"
            mode="multiple"
            allowClear
            placeholder="Input at most 5 stocks"
            option-label-prop="label"
            @select="onStockListSelect"
        >
          <a-select-option
              disabled
              style="color: steelblue; font-size: 16px"
          >
            <p style="text-align: left; width:30%; display: inline-block; padding-left: 2%"> <b>Stock code</b> </p>
            <p style="text-align: center; width:40%;  display: inline-block;"> <b>Company name</b></p>
            <p style="text-align: right; width:30%;  display: inline-block; padding-right: 2%"> <b>Industry</b> </p>
          </a-select-option>
          <a-select-option
              v-for='stock in stockList'
              :key='stock.ts_code'
              :label="stock.ts_code"
          >
            <p style="text-align: left; width:30%; display: inline-block; padding-left: 5%">{{ stock.ts_code }}</p>
            <p style="text-align: center; width:40%;  display: inline-block;">{{ stock.name }}</p>
            <p style="text-align: right; width:30%;  display: inline-block; padding-right: 5%">{{ stock.industry_name }}</p>
          </a-select-option>
        </a-select>
      </a-col>
      <a-col :span="2" class="first-row">
        <a-button
            shape="circle"
            type="primary"
            :loading="stockButtonLoading"
            :disabled="stockButtonDisabled"
            @click="onStockButtonClick"
        >
          <template #icon><SearchOutlined/></template>
        </a-button>
      </a-col>
    </a-row>

    <a-divider>Selected Period</a-divider>
    <a-row type="flex" justify="space-around" class="second-row" style="padding: 0px">
      <a-col :span="21" class="second-row">
        <a-range-picker
            style="width: 100%"
            v-model:value="periodRange"
            :disabledDate="periodDisabledRange"
            :ranges="periodPresetRange"
        />
      </a-col>
      <a-col :span="2" class="second-row">
        <a-button
            shape="circle"
            type="primary"
            :loading="periodButtonLoading"
            :disabled="periodButtonDisabled"
            @click="onPeriodButtonClick"
        >
          <template #icon><CalendarOutlined/></template>
        </a-button>
      </a-col>
    </a-row>

    <a-divider>Correlation Filter</a-divider>
    <a-row type="flex" justify="space-around" class="third-row" style="margin: -10px 0px 35px 0px; padding: 0px">
      <a-col :span="21" class="third-row">
        <a-slider
            style="align-content: center"
            range
            :tooltipVisible="false"
            v-model:value="correlationRange"
            :min="-1"
            :max="1"
            :step="0.05"
            :marks="correlationMarks"
            @change="onCorrelationSliderChange"
        />
      </a-col>
      <a-col :span="2" class="third-row">
        <a-button
            shape="circle"
            type="primary"
            :loading="correlationButtonLoading"
            :disabled="correlationButtonDisabled"
            @click="onCorrelationButtonClick"
        >
          <template #icon><FilterOutlined/></template>
        </a-button>
      </a-col>
    </a-row>

    <a-row type="flex" justify="space-around" class="forth-row" style="padding: 0px">
      <a-col :span="21">
        <a-table
            rowKey="ts_code"
            :scroll="{ y: 200, x: 450 }"
            :columns="stockListColumns"
            :data-source="correlatedStocks"
        />
      </a-col>
      <a-col :span="2">
        <a-button
            shape="circle"
            type="primary"
            :disabled="clusterButtonDisabled"
            @click="onClusterButtonClick"
        >
          <template #icon><SearchOutlined/></template>
        </a-button>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import moment from 'moment';
import 'moment/dist/locale/zh-cn';
import DataService from "@/utils/data-service";
import {CalendarOutlined, FilterOutlined, SearchOutlined, } from '@ant-design/icons-vue';

export default {
  name: 'ControlPanel',
  components: {
    SearchOutlined,
    CalendarOutlined,
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
      stockList: [{ts_code:'000001.SH', name:'上证指数', industry_name:'index'}],

      stockSelectionNumMax: 5,
      stockSelected: ['000652', '000538'],
      stockButtonLoading: false,

      periodRange: [moment.utc('2020-01-01', 'YYYY-MM-DD'), moment.utc('2020-06-30', 'YYYY-MM-DD')],
      periodPresetRange: {
        'All': [moment.utc('2011-01-01', 'YYYY-MM-DD'), moment.utc('2020-12-31', 'YYYY-MM-DD')],
        '3Y': [moment.utc('2018-01-01', 'YYYY-MM-DD'), moment.utc('2020-12-31', 'YYYY-MM-DD')],
        '1Y': [moment.utc('2020-01-01', 'YYYY-MM-DD'), moment.utc('2020-12-31', 'YYYY-MM-DD')],
        '3M': [moment.utc('2020-01-01', 'YYYY-MM-DD'), moment.utc('2020-03-31', 'YYYY-MM-DD')],
      },
      periodDisabledRange: (cur) => { return cur < moment.utc('2011-01-01', 'YYYY-MM-DD') || cur > moment.utc('2020-12-31', 'YYYY-MM-DD')},
      periodButtonLoading: false,
      periodButtonDisabled: true,

      correlationRange: [0.6, 1],
      correlationMarks: {0.6: '0.6', 0: '0', 1: '1'},
      correlationButtonLoading: false,
      correlationButtonDisabled: true,

      correlatedStocks: [],
      correlatedFilterIndustry: [],

      clusterButtonDisabled: true,
    }
  },
  computed: {
    stockButtonDisabled() {
      return !this.stockSelected.length;
    },
    stockListColumns() {
      return [
        {
          title: 'Stock Code',
          dataIndex: 'ts_code',
          key: 'ts_code',
        },
        {
          title: 'Company Name',
          dataIndex: 'name',
          key: 'name',
        },
        {
          title: 'Industry',
          dataIndex: 'industry_name',
          key: 'industry_name',
          filters: this.stockListIndustries,
          onFilter: (value, record) => record.industry_name.includes(value),
        },
      ];
    },
    stockListIndustries() {
      let set = Array.from(new Set(this.correlatedStocks.map(x => x.industry_name)));
      return set.map(x => {
        return {text: x, value: x};
      });
    },
  },
  watch: {
    periodRange: function() {
      this.$emit('update-period-range', this.periodRange);
    }
  },
  mounted: function () {
    DataService.get('get_stock_list', data => {
      console.log(data);
      this.stockList = data;
      
    })

  },
  methods: {
    onStockListSelect() {
      if ( this.stockSelected.length > this.stockSelectionNumMax ) {
        this.stockSelected.splice(this.stockSelectionNumMax,1);
      }
    },
    onStockButtonClick() {
      this.stockButtonLoading = !this.stockButtonLoading;
      DataService.post('set_stocks', this.stockSelected,(confirm) => {
        this.stockButtonLoading = !this.stockButtonLoading;
        if ( confirm ) {
          this.periodButtonDisabled = false;
        } else {
          this.stockSelected = []
        }
      });
    },
    onPeriodButtonClick() {
      this.periodButtonLoading = !this.periodButtonLoading;
      DataService.post('set_period', this.periodRange,(confirm) => {
        this.periodButtonLoading = !this.periodButtonLoading;
        if ( confirm ) {
          this.correlationButtonDisabled = false;
        }
      });
    },
    onCorrelationSliderChange(val) {
      this.correlationMarks = { 0: '0' };
      this.correlationMarks[val[0]] = ''+val[0];
      this.correlationMarks[val[1]] = ''+val[1];
    },
    onCorrelationButtonClick() {
      this.correlationButtonLoading = !this.correlationButtonLoading;
      DataService.post('set_correlation', this.correlationRange,(data) => {
        this.correlationButtonLoading = !this.correlationButtonLoading;
        this.clusterButtonDisabled = false;
        this.correlatedStocks = data;
      });
    },
    onClusterButtonClick() {
      this.$emit('get-correlation-matrix');
    },
  }
}
</script>

<style scoped>

.first-row {
  height: 30px;
}
.second-row {
  height: 30px;
}
.third-row {
  height: 30px;
}
.forth-row {
  height: 315px;
}
</style>
