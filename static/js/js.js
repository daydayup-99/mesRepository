$(window).on('load', function () {
    // 当页面上的所有资源（包括图片）都加载完成后执行的代码
    $(".loading").fadeOut(); // 淡出具有 "loading" 类的元素
});
$(function () {
    echarts_3()
    echarts_5()
    echarts_9()
})

function echarts_3() {
    // 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.getElementById('echart3'));

    // 模拟数据，你需要替换为实际的数据
    var dates = ['2022-03-01', '2022-03-02', '2022-03-03', '2022-03-04', '2022-03-05', '2022-03-06', '2022-03-07'];
    var capacities = [100, 120, 90, 150, 80, 110, 130];

    // 设置图表选项
    option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                crossStyle: {
                    color: '#999'
                }
            }
        },
        toolbox: {
            feature: {
                dataView: {show: true, readOnly: false},
                magicType: {show: true, type: ['line', 'bar']},
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        legend: {
            data: ['板数', '产能']
        },
        xAxis: [
            {
                type: 'category',
                data: ['机台1', '机台2', '机台3', '机台4', '机台5', '机台6', '机台7'],
                axisPointer: {
                    type: 'shadow'
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                name: '板数',
                min: 0,
                max: 20000, // 你需要根据实际情况调整最大值
                interval: 4000,
                axisLabel: {
                    formatter: '{value} 板'
                }
            },
            {
                type: 'value',
                name: '产能',
                min: 0,
                max: 3000, // 你需要根据实际情况调整最大值
                interval: 600,
                axisLabel: {
                    formatter: '{value} 产能'
                }
            }
        ],
        series: [
            {
                name: '板数',
                type: 'bar',
                tooltip: {
                    valueFormatter: function (value) {
                        return value + ' 板';
                    }
                },
                data: [
                    2000, 4000, 6000, 8000, 1000, 12000, 14000
                ]
            },
            {
                name: '产能',
                type: 'line',
                yAxisIndex: 1,
                tooltip: {
                    valueFormatter: function (value) {
                        return value + ' 产能';
                    }
                },
                data: [500, 1000, 1500, 2000, 2500, 3000, 2500]
            }
        ]
    };
    // 设置图表选项
    myChart.setOption(option);

    // 监听窗口大小变化，自适应图表
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}


function echarts_5() {
    // 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.getElementById('echart5'));
    option = {
        tooltip: {  //提示框设置
            trigger: 'axis',
            axisPointer: {    //设置横线的样式
                lineStyle: {
                    color: '#dddc6b'
                }
            },
            textStyle: {      //设置提示框的对齐方式
                align: 'left'
            }
        },
        grid: {   //设置内容区域距离周边的距离
            left: '10',
            top: '20',
            right: '30',
            bottom: '10',
            containLabel: true
        },
        toolbox: {
            show: false
        },
        legend: {
            show: false
        },
        xAxis: [
            {
                type: 'category',
                data: ['机台2', '机台4', '机台6', '机台8', '机台10', '机台12', '机台14', '机台16', '机台18', '机台20', '机台22', '机台24'],
                axisPointer: {
                    type: 'shadow'
                },
                axisTick: {           //刻度
                    show: true //不显示刻度线
                },
                axisLine: {
                    lineStyle: {
                        color: 'rgba(255,255,255,.2)'  //轴线的颜色
                    }
                },
                axisLabel: {          //轴线字体样式设置
                    textStyle: {
                        color: "rgba(255,255,255,.6)",
                        fontSize: 14,
                    }
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                //      min: 0,
                //      max: 0,
                //      interval: 0,
                axisLabel: {
                    formatter: '{value}',
                    textStyle: {
                        color: "rgba(255,255,255,.6)",
                        fontSize: 14,
                    }
                },
                splitLine: {          //去除背景网格线
                    show: false
                },
                axisTick: {   //刻度
                    show: false         //不显示刻度线
                },
                axisLine: {
                    lineStyle: {
                        color: '#fff'  //轴线的颜色
                    }
                }
            },
            {
                type: 'value',
                min: 0,
                max: 0,
                interval: 0,
                axisLabel: {
                    formatter: '{value}',
                    textStyle: {
                        fontFamily: 'ArialMT',
                        fontSize: '12',
                        color: '#86A5C3',
                    }
                },
                splitLine: {      //去除背景网格线
                    show: false
                },
                axisTick: {       //刻度
                    show: false     //不显示刻度线
                },
                axisLine: {
                    lineStyle: {
                        color: '#1E2240'  //轴线的颜色
                    }
                }
            }
        ],
        series: [
            { //柱状(左边数据)
                name: '卡口进',
                type: 'bar',
                data: [0.2, 0.2, 0.3, 0.23, 0.12, 0.8, 0.5, 0.9, 0.23, 0.12, 0.8, 0.8],
                itemStyle: {    //柱状图的背景色
                    normal: {
                        color: '#0060D1'
                    }
                },
                barWidth: 6
            },
            { //柱状(左边数据)
                name: '卡口出',
                type: 'bar',
                data: [0.112, 0.312, 0.123, 0.213, 0.112, 0.312, 0.123, 0.213, 0.123, 0.213, 0.112, 0.213],
                itemStyle: {    //柱状图的背景色
                    normal: {
                        color: '#00D2FF'
                    }
                },
                barWidth: 6
            },
            { //折线(右边数据)
                name: '总量',
                type: 'line',
                smooth: true,
                yAxisIndex: 1,
                data: [0.112, 0.312, 0.3, 0.6, 0.8, 0.2, 0.7, 0.5, 0.3, 0.6, 0.8, 0.6],
                itemStyle: {    //折线颜色
                    normal: {
                        color: '#2A47F8'
                    }
                }
            }
        ]
    };
    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}

function echarts_9() {
    // 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.getElementById('echart9'))

    option = {
        series: [
            {
                type: 'gauge',
                center: ['50%', '50%'],
                // 调整显示圆弧的弧度，也就是可以调整显示的圆圈
                startAngle: 240,
                endAngle: -60,
                min: 0,
                max: 100,
                splitNumber: 12,
                itemStyle: {
                    // 圆弧刻度的颜色,这样只是设置一个颜色
                    // color: '#ffabcd',
                    // 颜色渐变
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 1,
                        y2: 0,
                        colorStops: [{
                            offset: 0, color: '#F8ED41' // 0% 处的颜色
                        }, {
                            offset: 1, color: '#E4951E' // 100% 处的颜色
                        }],
                        global: false // 默认为 false
                    }
                },
                // 显示进度
                progress: {
                    show: true,
                    width: 10
                },
                pointer: {
                    //关闭指示器
                    show: false
                },
                axisLine: {
                    lineStyle: {
                        width: 10,
                        // 阴影的颜色
                        shadowColor: 'rgba(255,0, 0, 1)',
                        // 阴影的宽度
                        shadowBlur: 22,
                        // 阴影的x偏移量
                        shadowOffsetX: 0,
                        // 底圈的颜色
                        color: [[1, "rgba(255,255,255,9)"]],
                    }
                },
                // 刻度线
                axisTick: {
                    distance: -35,
                    splitNumber: 5,
                    lineStyle: {
                        width: 1,
                        color: '#ffabcd'
                    }
                },
                // 外圈刻度分割线
                splitLine: {
                    distance: -52,
                    length: 14,
                    lineStyle: {
                        // 设置成0不要刻度分割线
                        width: 0,
                        color: '#999'
                    }
                },
                // 刻度数字
                axisLabel: {
                    distance: -20,
                    color: '#999',
                    // 设置成0不要刻度数字
                    fontSize: 0
                },
                anchor: {
                    show: false
                },
                title: {
                    show: false
                },
                detail: {
                    valueAnimation: true,
                    width: '60%',
                    lineHeight: 40,
                    borderRadius: 8,
                    offsetCenter: [0, '0%'],
                    fontSize: 20,
                    fontWeight: 'bolder',
                    formatter: '一次良率\n{value} %',
                    color: '#f4e925' //inherit表示和图表颜色一致
                },
                data: [
                    {
                        value: 20
                    }
                ]
            }
        ]
    };
    setInterval(function () {
        const random = +(Math.random() * 100).toFixed(2);
        myChart.setOption({
            series: [
                {
                    data: [
                        {
                            value: random
                        }
                    ]
                },
                {
                    data: [
                        {
                            value: random
                        }
                    ]
                }
            ]
        });
    }, 2000);

    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}

function MacMeanAi(macnameData,macfMeanData,macfMeanAiData) {
    // 基于准备好的dom，初始化echarts实例
     var myChart = echarts.init(document.getElementById('echart6'));
    option = {
        tooltip: {  //提示框设置
            trigger: 'axis',
            axisPointer: {    //设置横线的样式
                lineStyle: {
                    color: '#dddc6b'
                }
            },
            textStyle: {      //设置提示框的对齐方式
                align: 'left'
            }
        },
        grid: {   //设置内容区域距离周边的距离
            left: '10',
            top: '20',
            right: '30',
            bottom: '10',
            containLabel: true
        },
        toolbox: {
            show: false
        },
        legend: {
            show: false
        },
        xAxis: [
            {
                type: 'category',
                data: macnameData,
                axisPointer: {
                    type: 'shadow'
                },
                axisTick: {           //刻度
                    show: true //不显示刻度线
                },
                axisLine: {
                    lineStyle: {
                        color: 'rgba(255,255,255,.2)'  //轴线的颜色
                    }
                },
                axisLabel: {         //轴线字体样式设置
                    rotate: 45,
                    textStyle: {
                        color: "rgba(255,255,255,.6)",
                        fontSize: 14,
                    }
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                //      min: 0,
                //      max: 0,
                //      interval: 0,
                axisLabel: {
                    formatter: '{value}',
                    textStyle: {
                        color: "rgba(255,255,255,.6)",
                        fontSize: 14,
                    }
                },
                splitLine: {          //去除背景网格线
                    show: false
                },
                axisTick: {   //刻度
                    show: false         //不显示刻度线
                },
                axisLine: {
                    lineStyle: {
                        color: '#fff'  //轴线的颜色
                    }
                }
            },
            {
                type: 'value',
                min: 0,
                max: 0,
                interval: 0,
                axisLabel: {
                    formatter: '{value}',
                    textStyle: {
                        fontFamily: 'ArialMT',
                        fontSize: '12',
                        color: '#86A5C3',
                    }
                },
                splitLine: {      //去除背景网格线
                    show: false
                },
                axisTick: {       //刻度
                    show: false     //不显示刻度线
                },
                axisLine: {
                    lineStyle: {
                        color: '#1E2240'  //轴线的颜色
                    }
                }
            }
        ],
        series: [
            { //柱状(左边数据)
                name: '总报点',
                type: 'bar',
                data: macfMeanData,
                itemStyle: {    //柱状图的背景色
                    normal: {
                        color: '#60CDC9FF'
                    }
                },
                barWidth: 6
            },
            { //柱状(右边数据)
//                name: 'AI后报点',
                name: 'AI真点报点',
                type: 'bar',
                data: macfMeanAiData,
                itemStyle: {    //柱状图的背景色
                    normal: {
                        color: '#ADD8E6'
                    }
                },
                barWidth: 6
            },
        ]
    };
    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}

function MacAiPass(macnameData,macAiData) {
    // 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.getElementById('echart7'));
    option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                lineStyle: {
                    color: '#dddc6b'
                }
            }
        },
        grid: {
            left: '10',
            top: '20',
            right: '30',
            bottom: '10',
            containLabel: true
        },

        xAxis: [{
            type: 'category',
            boundaryGap: false,
            axisLabel: {
                rotate: 45,
                textStyle: {
                    color: "rgba(255,255,255,.6)",
                    fontSize: 14,
                },
            },
            axisLine: {
                lineStyle: {
                    color: 'rgba(255,255,255,.2)'
                }

            },

            data: macnameData

        }, {

            axisPointer: {show: false},
            axisLine: {show: false},
            position: 'bottom',
            offset: 20,
        }],

        yAxis: [{
            type: 'value',
            axisTick: {show: false},
            splitNumber: 4,
            axisLine: {
                lineStyle: {
                    color: 'rgba(255,255,255,.1)'
                }
            },
            axisLabel: {
                textStyle: {
                    color: "rgba(255,255,255,.6)",
                    fontSize: 16,
                },
            },

            splitLine: {
                lineStyle: {
                    color: 'rgba(255,255,255,.1)',
                    type: 'dotted',
                }
            }
        }],
        series: [
            {
                name: '假点去除率',
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 5,
                //        showSymbol: false,
                lineStyle: {

                    normal: {
                        color: 'rgba(31, 174, 234, 1)',
                        width: 2
                    }
                },
                itemStyle: {
                    normal: {
                        color: '#1f7eea',
                        borderColor: 'rgba(31, 174, 234, .1)',
                        borderWidth: 5
                    }
                },
                data: macAiData

            },

        ]

    };
    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}

function ShowErrRate(stdata) {
    var myChart = echarts.init(document.getElementById('echart8'));
    option = {
        // 控制提示
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        // 控制图表
        series: [
            {
                name: '缺陷类型', // 图表名称改为缺陷类型
                type: 'pie',
                radius: ['10%', '70%'],
                center: ['50%', '50%'],
                roseType: 'radius',
                data: stdata,
                label: {
                    fontFamily: 'Roboto, sans-serif',
                    fontSize: 10,
                    fontWeight: 500,  // 500表示中等字重，可以根据需要调整
                    lineHeight: 1.5,   // 行高，可以根据需要调整
                    WebkitFontSmoothing: 'antialiased'
                },
                labelLine: {
                    length: 8,
                    length2: 10
                }
            }
        ],
        color: ['#006cff', '#60cdc9', '#ed8884', '#ff9f7f', '#0096ff', '#9fe6b8', '#32c5e9', '#1d9dff']
    };
    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
}

function ShowErrNum(stdata){
    const chartDom = document.getElementById('echart4')
    var myChart = echarts.init(chartDom);
    var defectData = stdata

    //
//    chartDom.style.position = "relative"
//        const div = document.createElement("div")
//        div.style.width = "100%"
//        div.style.height = "100%"
//        div.style.backgroundColor = "#ccc"
//        div.style.position = "absolute"
//        div.style.top = 0
//        div.style.left = "100%"
//        div.style.zIndex = 999
//        div.style.display = "none"
//        div.onclick = ()=>{
//            div.style.display = "none"
//        }
//        chartDom.appendChild(div)

    option = {
//         tooltip: {
//            trigger: 'axis'
//        },
        grid: {
            left: '0',
            top: '0',
            right: '0',
            bottom: '0%',
            containLabel: true
        },
        xAxis: {
            show: false
        },
        yAxis: [{
            show: true,
            data: defectData.map(item => item.name),
            inverse: true,
            axisLine: {show: false},
            splitLine: {show: false},
            axisTick: {show: false},
            axisLabel: {
                textStyle: {
                    color: '#fff'
                },
            },
        }, {
            show: false,
            inverse: true,
            data: defectData.map(item => item.value),
            axisLabel: {textStyle: {color: '#fff'}},
            axisLine: {show: false},
            splitLine: {show: false},
            axisTick: {show: false},
        }],
        series: [{
            name: '条',
            type: 'bar',
            yAxisIndex: 0,
            data: defectData.map(item => item.value),
            barWidth: 15,
            itemStyle: {
                normal: {
                    barBorderRadius: 50,
                    color: '#1089E7',
                }
            },
            label: {
                normal: {
                    show: true,
                    position: 'right',
                    formatter: '{c}',
                    textStyle: {color: 'rgba(255,255,255,.5)'}
                }
            },
        }]
    };

// 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);
    window.addEventListener("resize", function () {
        myChart.resize();
    });
    myChart.off('click');
    myChart.on('click', function (params) {
//        console.log("res:"+stdata);

//        div.style.display = "block"
//        var chart = echarts.init(div);
//        chart.setOption(option)
        // 弹框显示点击的柱状图对应的数据
        const errName = params.name;
        MacErrJob(errName, function(stdata) {
            // 弹框显示点击的柱状图对应的数据
            var resultText = "缺陷名: " + errName + "\n";

            // 遍历 stdata 数组，提取 Job 和 MachineID
            for (var i = 0; i < stdata.length; i++) {
                var item = stdata[i];
                resultText += "膜面，料号，缺陷料号占比: " + item['Job'] + "\n机台号: " + item['MachineID'] + "\n";
            }

            // 弹出包含所有信息的提示框
            alert(resultText);

        });
        // 你也可以在这里显示自定义弹框，或者使用模态框等其他形式
    });
}


function MacErrJob(errName,callback) {
    console.log("ErrName: " + errName)
    $.ajax({
        url: '/MacErrJob',
        type: 'GET',
        async: false,
        success: function (response) {
            var Data = JSON.parse(response);
            var resK = []
            var resV = []
            var res = []
            for (var i = 0; i < Data.length; i++)
            {
                for (var j = 0; j < Data[i].length; j++)
                {
                    var item = Data[i][j]
                    if (item.hasOwnProperty(errName))
                    {
                        var errData = item[errName];
                        res.push({
                            Job: errData['Job'],         // 假设 'Job' 是对应的字段
                            MachineID: errData['MachineID']  // 假设 'MachineID' 是对应的字段
                        });
                    }
                }
            }
            callback(res);
        },
        error: function (xhr, status, error) {
            // 处理请求错误
            console.error('Request error:', error);
        }
    });
}










