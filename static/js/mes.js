/**
 * Created by Administrator on 2017/4/25.
 */
//YCJ
function buildBarVO(startDate, endDate, type) {
    var myChart = echarts.init($("#containerBar")[0]);
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        calculable: true,
        xAxis: [
            {
                type: 'category',
                data: [],
                axisLabel: {
                    rotate: 40,
                    interval: 0
                },
                name: '批量号',
                nameTextStyle: {
                    fontWeight: 300,
                    fontSize: 9,
                    Align: 'top'
                },
            }
        ],

        yAxis: [
            {
                type: 'value',
                name: '不良率',
                nameTextStyle: {
                    fontWeight: 300,
                    fontSize: 9,
                    Align: 'top'
                },
            }
        ],
        series: [
            {
                type: 'bar',
                barWidth: '30',
                data: [],
                itemStyle: {
                    normal: {
                        color: "#269fec"
                    }
                }

            }
        ],
        dataZoom: [
            {
                type: 'slider',
                show: true,
                start: 0,
                end: 100,
                height: 10,//组件高度
                bottom: 0,
                borderColor: "#000",
                fillerColor: '#269cdb',
            }
        ],
    };
    function updateChart(startDate, endDate, type) {
        var url = 'http://192.168.0.199:10001/barVO?startDate=' + startDate + '&endDate=' + endDate + '&type=' + type;

        // 发送GET请求获取API数据，并设置超时时间为10秒
        $.ajax({
            url: url,
            type: 'GET',
            timeout: 10000, // 设置超时时间为10秒
            success: function (data) {
                var categoryData = data.category; // 提取category数组
                var valuesData = data.Values; // 提取Values数组
                console.log(categoryData);
                // 更新X轴数据
                option.xAxis[0].data = categoryData;

                // 更新Y轴数据
                option.series[0].data = valuesData;

                myChart.setOption(option);

                // //创建表格
                // let headerRow = document.getElementById('barTable_row1');
                // console.log(headerRow);
                // // 根据API返回的数据动态创建表格单元格
                // for (let i = 0; i < data.category.length; i++) {
                //     let cell = headerRow.insertCell();
                //     cell.textContent = data.category[i];
                // }

                // let rateRow = document.getElementById('barTable_row2');

                // for (let i = 0; i < data.Values.length; i++) {
                //     let cell = rateRow.insertCell();
                //     cell.textContent = data.Values[i];
                // }
            },
            error: function (xhr, status, error) {
                console.log("Error occurred: " + error);
            }
        });
    }
    // 初始化加载图表
    updateChart(startDate, endDate, type);
};


function buildLineVO(startDate, endDate, type) {
    var myChart = echarts.init($("#containerLine")[0]);
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        legend: {
            data: []
        },
        xAxis: [
            {
                type: 'category',
                data: [],
                rotate: 40, interval: 0,
                name: 'Lot',
                nameTextStyle: {
                    fontWeight: 300,
                    fontSize: 9,
                    Align: 'top',
                },
            }
        ],

        yAxis: [
            {
                type: 'value',
                min: 0,
                max: 100,
                interval: 10,
                name: '假点率（%）',
                nameTextStyle: {
                    fontWeight: 300,
                    fontSize: 9,
                    Align: 'top'
                },
            }
        ],
        series: [
            {
                name: 'Lot假点率',
                type: 'line',
                barWidth: '10',
                data: [],
                itemStyle: {
                    normal: {
                        color: "#269fec"
                    }
                }

            }
        ],
        dataZoom: [
            {
                type: 'slider',
                show: true,
                start: 0,
                end: 100,
                height: 10,//组件高度
                bottom: 0,
                borderColor: "#000",
                fillerColor: '#269cdb',
            }
        ]
    };
    // 发送GET请求获取API数据
    function updateChart(startDate, endDate, type) {
        var url = 'http://192.168.0.199:10001/lineFalseVO?startDate=' + startDate + '&endDate=' + endDate + '&type=' + type;

        // 发送GET请求获取API数据，并设置超时时间为10秒
        $.ajax({
            url: url,
            type: 'GET',
            timeout: 10000, // 设置超时时间为10秒
            success: function (data) {
                var categoryData = data.category; // 提取category数组
                var valuesData = data.Values; // 提取Values数组
                // 更新X轴数据
                option.xAxis[0].data = categoryData;

                // 更新Y轴数据
                option.series[0].data = valuesData;
                myChart.setOption(option);
            },
            error: function (xhr, status, error) {
                console.log("Error occurred: " + error);
            }
        });
    }
    // 初始化加载图表
    updateChart(startDate, endDate, type);
};


function buildLineFalseVO(startDate, endDate, type) {
    var myChart = echarts.init($("#containerLineFalse")[0]);
    var option = {
        title: {
            text: '时间段内整体一次/二次良率',
            left: 'center',
            top: 0,
            textStyle: {
                color: '#555555'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        legend: {
            type: 'plain',
            orient: 'vertical',
            right: 10,
            top: 20,
            bottom: 20,
            data: ['一次良率', '二次良率'],
            show: true//图例是否显示
        },
        calculable: true,
        xAxis: [
            {
                type: 'category',
                data: [],
                rotate: 40, interval: 0,
                name: '时间',
                nameTextStyle: {
                    fontWeight: 300,
                    fontSize: 9,
                    Align: 'top'
                },
            },
        ],
        yAxis: [
            {
                type: 'value',
                min: 0,
                max: 100,
                interval: 20,
                name: '良率(%)',
                nameTextStyle: {
                    fontWeight: 300,
                    fontSize: 9,
                    Align: 'top'
                },
            },
        ],
        series: [
            {
                name: '一次良率',
                itemStyle: { normal: { label: { show: true } } },
                barWidth: '30',
                data: [],
                type: 'line',
                itemStyle: {
                    normal: {
                        color: "#269fec"
                    }
                }
            },
            {
                name: '二次良率',
                itemStyle: { normal: { label: { show: true } } },
                barWidth: '30',
                data: [],
                type: 'line',
                itemStyle: {
                    normal: {
                        color: "#ffe400"
                    }
                }
            },
        ]
    };

    function updateChart(startDate, endDate, type) {
        var url = 'http://192.168.0.199:10001/lineGRByTimeVO?startDate=' + startDate + '&endDate=' + endDate + '&type=' + type;

        // 发送GET请求获取API数据，并设置超时时间为10秒
        $.ajax({
            url: url,
            type: 'GET',
            timeout: 10000, // 设置超时时间为10秒
            success: function (data) {
                var Dates = data.Dates; // 提取Adates数组
                var valuesData = data.Values; // 提取Values数组
                var valuesData2 = data.Values2; // 提取Values2数组
                // 更新X轴数据
                option.xAxis[0].data = Dates;

                // 更新Y轴数据
                option.series[0].data = valuesData;
                option.series[1].data = valuesData2;
                myChart.setOption(option);
            },
            error: function (xhr, status, error) {
                console.log("Error occurred: " + error);
            }
        });
    }

    // 初始化加载图表
    updateChart(startDate, endDate, type);
};

function buildParetoVO(startDate, endDate, type) {
    var myChart = echarts.init($("#containerParetoErrType")[0]);
    var option = {
        title: {
            text: '时间段内整体缺陷种类',
            left: 'center',
            top: 0,
            textStyle: {
                color: '#555555'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        legend: {
            type: 'plain',
            orient: 'vertical',
            right: 10,
            top: 20,
            bottom: 20,
            data: ['缺陷个数', '缺陷百分比'],
            show: true//图例是否显示
        },
        //toolbox: {
        //    show : true,
        //    //orient: 'vertical',
        //    x: 'right',
        //    y: 'top',
        //    feature : {
        //        mark : {show: true},
        //        dataView : {show: true, readOnly: false},
        //        magicType : {show: true, type: ['line', 'bar', 'stack', 'tiled']},
        //        restore : {show: true},
        //        saveAsImage : {show: true}
        //    }
        //},
        calculable: true,
        xAxis: [
            {
                type: 'category',
                data: [],
                axisLabel: {
                    interval: 0,
                    rotate: 40,
                },
                name: '缺陷种类',
                nameTextStyle: {
                    fontWeight: 600,
                    fontSize: 18,
                    Align: 'top',
                },
            },
        ],
        yAxis: [{
            type: 'value',
            name: '缺陷个数',
            nameTextStyle: {
                fontWeight: 600,
                fontSize: 18,
                Align: 'top',
            },
        },
        {
            type: 'value',
            min: 0,
            max: 100,
            interval: 20,
        }],
        series: [
            {
                name: '缺陷个数',
                itemStyle: { normal: { label: { show: true } } },
                barWidth: '30',
                data: [],
                type: 'bar',
            },
            {
                name: '缺陷百分比',
                itemStyle: { normal: { label: { show: true } } },
                barWidth: '30',
                data: [],
                type: 'line',
                yAxisIndex: 1
            },
        ],
        dataZoom: [
            {
                type: 'slider',
                show: true,
                start: 0,
                end: 100,
                height: 10,//组件高度
                bottom: 0,
                borderColor: "#000",
                fillerColor: '#269cdb',
            }]
    };
    function updateChart(startDate, endDate, type) {
        var url = 'http://192.168.0.199:10001/paretoErrTypeVO?startDate=' + startDate + '&endDate=' + endDate + '&type=' + type;
        $.ajax({
            url: url,
            type: 'GET',
            timeout: 10000, // 设置超时时间为5秒
            success: function (data) {
                var categoryData = data.category; // 提取Adates数组
                var valuesData = data.Values; // 提取Values数组
                var valuesData2 = data.Values2; // 提取Values2数组
                // 更新X轴数据
                option.xAxis[0].data = categoryData;

                // 更新Y轴数据
                option.series[0].data = valuesData;
                option.series[1].data = valuesData2;
                myChart.setOption(option);
            },
            error: function (xhr, status, error) {
                console.log("Error occurred: " + error);
            }
        });
    }
    // 初始化加载图表
    updateChart(startDate, endDate, type);
};

function sendRequest() {
    var start_time = $('#startDate').val();
    var end_time = $('#endDate').val();
    var type = $('#type').val();
    buildBarVO(start_time, end_time, type);
    buildLineVO(start_time, end_time, type);
    buildLineFalseVO(start_time, end_time, type);
    buildParetoVO(start_time, end_time, type);
}

function initDate() {
    let currentDate = new Date();
    let previousDate = new Date(currentDate);
    previousDate.setDate(currentDate.getDate() - 1);
    let previousDateString = previousDate.toISOString().split('T')[0];
    let currentDateString = currentDate.toISOString().split('T')[0];

    document.getElementById('startDate').value = previousDateString;
    document.getElementById('endDate').value = currentDateString;
    console.log(1);
}
$(document).ready(function () {
    sendRequest();
    initDate();
    $('#updateEcharts').click(function () {
        sendRequest();
    });

});