import axios from 'axios'

let DataService = {
  DATA_SERVER_URL: 'http://127.0.0.1:5000/',

  // HTTP GET request
  get(path, callback){
    axios.get(`${this.DATA_SERVER_URL}/${path}`)
      .then(response => {
        callback(response.data)
      }, errResponse => {
        console.log(errResponse)
      })
  },

  // HTTP POST request
  post(path, param, callback){
    axios.post(`${this.DATA_SERVER_URL}/${path}`, param)
      .then(response => {
        callback(response.data)
      }, errResponse => {
        console.log(errResponse)
      })
  },
}

export default DataService;
