/**
 * Created by Administrator on 2017/4/25.
 */
function generateAi(dates,fAiData) {
    var myChart = echarts.init($("#container1")[0]);
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['假点去除率'],
            textStyle: {
                color: '#333'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: dates,
            axisLabel: {
                rotate: 45, // 将标签旋转45度
                show: true,
                textStyle: {
                    color: '#333',

                }
            }
        },
        yAxis: [
            {
                type: 'value',
                name: '假点去除率',
                max: 100,  // 设置最大值为 100
                interval: 10,
                axisLabel: {
                    show: true,
                    formatter: '{value}%'
                },
            }
        ],
        dataZoom: [
            {
                type: 'slider',  // 设置为滑动条类型
                show: false
            },
            {
                type: 'inside',  // 设置为内部滑动条类型
                start: 0,  // 数据窗口的起始位置百分比
                end: 100,   // 数据窗口的结束位置百分比
                filterMode: 'filter'  // 设置为过滤模式，即在缩放时过滤数据
            }
        ],
        series: [
            {
                name: '假点去除率',
                type: 'line',
                max: 100,
                data: fAiData,
                itemStyle: {
                    color: '#b1de6a'
                },
                label: {
                    show: true,
                    formatter: '{c}%' // 显示百分比
                },
                toolbox: {
                    feature: {
                        dataZoom: {  // 数据区域缩放工具
                            yAxisIndex: false  // 不允许对纵坐标轴进行缩放
                        },
                        dataView: {  // 数据视图工具
                            readOnly: true  // 设置为只读，用户无法编辑数据视图
                        },
                        magicType: {  // 图表类型切换工具
                            type: ['line', 'bar']  // 设置支持切换的图表类型
                        },
                        restore: {},  // 还原工具
                        saveAsImage: {}  // 保存为图片工具
                    }
                },
            }
        ]
    };
    myChart.setOption(option);
    window.addEventListener("resize", (event) => {
        myChart.resize()
    });
}

function generateAllAi(dates,fAllAiData) {
   var myChart = echarts.init($("#container2")[0]);
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['总过滤率'],
            textStyle: {
                color: '#333'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: dates,
            axisLabel: {
                rotate: 45, // 将标签旋转45度
                show: true,
                textStyle: {
                    color: '#333',

                }
            }
        },
        yAxis: [
            {
                type: 'value',
                name: '总过滤率',
                max: 100,  // 设置最大值为 100
                interval: 10,
                axisLabel: {
                    show: true,
                    formatter: '{value}%'
                },
            }
        ],
        dataZoom: [
            {
                type: 'slider',  // 设置为滑动条类型
                show: false
            },
            {
                type: 'inside',  // 设置为内部滑动条类型
                start: 0,  // 数据窗口的起始位置百分比
                end: 100,   // 数据窗口的结束位置百分比
                filterMode: 'filter'  // 设置为过滤模式，即在缩放时过滤数据
            }
        ],
        series: [
            {
                name: '总过滤率',
                type: 'line',
                max: 100,
                data: fAllAiData,
                itemStyle: {
                    color: '#b1de6a'
                },
                label: {
                    show: true,
                    formatter: '{c}%' // 显示百分比
                },
                toolbox: {
                    feature: {
                        dataZoom: {  // 数据区域缩放工具
                            yAxisIndex: false  // 不允许对纵坐标轴进行缩放
                        },
                        dataView: {  // 数据视图工具
                            readOnly: true  // 设置为只读，用户无法编辑数据视图
                        },
                        magicType: {  // 图表类型切换工具
                            type: ['line', 'bar']  // 设置支持切换的图表类型
                        },
                        restore: {},  // 还原工具
                        saveAsImage: {}  // 保存为图片工具
                    }
                },
            }
        ]
    };
    myChart.setOption(option);
    window.addEventListener("resize", (event) => {
        myChart.resize()
    });
}

function generateOKPass(dates,fPassData) {
   var myChart = echarts.init($("#container3")[0]);
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['一次Pass率'],
            textStyle: {
                color: '#333'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: dates,
            axisLabel: {
                rotate: 45, // 将标签旋转45度
                show: true,
                textStyle: {
                    color: '#333',

                }
            }
        },
        yAxis: [
            {
                type: 'value',
                name: '一次Pass率',
                max: 100,  // 设置最大值为 100
                interval: 10,
                axisLabel: {
                    show: true,
                    formatter: '{value}%'
                },
            }
        ],
        dataZoom: [
            {
                type: 'slider',  // 设置为滑动条类型
                show: false
            },
            {
                type: 'inside',  // 设置为内部滑动条类型
                start: 0,  // 数据窗口的起始位置百分比
                end: 100,   // 数据窗口的结束位置百分比
                filterMode: 'filter'  // 设置为过滤模式，即在缩放时过滤数据
            }
        ],
        series: [
            {
                name: '一次Pass率',
                type: 'line',
                max: 100,
                data: fPassData,
                itemStyle: {
                    color: '#b1de6a'
                },
                label: {
                    show: true,
                    formatter: '{c}%' // 显示百分比
                },
                toolbox: {
                    feature: {
                        dataZoom: {  // 数据区域缩放工具
                            yAxisIndex: false  // 不允许对纵坐标轴进行缩放
                        },
                        dataView: {  // 数据视图工具
                            readOnly: true  // 设置为只读，用户无法编辑数据视图
                        },
                        magicType: {  // 图表类型切换工具
                            type: ['line', 'bar']  // 设置支持切换的图表类型
                        },
                        restore: {},  // 还原工具
                        saveAsImage: {}  // 保存为图片工具
                    }
                },
            }
        ]
    };
    myChart.setOption(option);
    window.addEventListener("resize", (event) => {
        myChart.resize()
    });
}

function generateMean(dates,fMeaAllData,fMeaAiData){
    var myChart = echarts.init($("#container4")[0]);
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                crossStyle: {
                    color: '#999'
                }
            }
        },
        legend: {
            icon: 'rect',
            itemWidth: 10,
            itemHeight: 4,
            itemGap: 24,
            data: ['AI前', 'AI后'],
            textStyle: {
                color: '#c1dafc',
                fontSize: '12'
            },
            right: '30%'
        },
        xAxis: [
            {
                type: 'category',
                data:  dates,
                axisPointer: {
                     show: true,
                    rotate: 45,
                },
                axisLabel: {
                    rotate: 45,
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                name: '平均报点：',
                axisLabel: {
                    formatter: '{value}'
                }
            }
        ],
        series: [
            {
                name: 'AI前',
                type: 'bar',
                barWidth: '10%',
                data: fMeaAllData,
                itemStyle: {
                    color: '#b1de6a'  // 单独设置数据系列的颜色
                },
                label: {
                show: true,  // 显示标签
                position: 'top',  // 标签位置：顶部
                formatter: '{c}', // 标签内容格式
                color: '#333'  // 标签文字颜色
            }
            },
            {
                name: 'AI后',
                type: 'bar',
                barWidth: '10%',
                data: fMeaAiData,
                itemStyle: {
                    color: '#4ab0ee'  // 单独设置数据系列的颜色
                },
                label: {
                show: true,  // 显示标签
                position: 'top',  // 标签位置：顶部
                formatter: '{c}', // 标签内容格式
                color: '#333'  // 标签文字颜色
            }
            }
        ],
         dataZoom: [
            {
                type: 'slider',  // 设置为滑动条类型
                show: false
            },
            {
                type: 'inside',  // 设置为内部滑动条类型
                start: 0,  // 数据窗口的起始位置百分比
                end: 100,   // 数据窗口的结束位置百分比
                filterMode: 'filter'  // 设置为过滤模式，即在缩放时过滤数据
            }
        ],
    };
    myChart.setOption(option);
    window.addEventListener("resize", (event) => {
        myChart.resize()
    });
}

function generateJobMean(jobname,fJObMeanAll,fJObMeanAi){
    var myChart = echarts.init($("#container5")[0]);
  var option = {
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross',
            crossStyle: {
                color: '#999'
            }
        }
    },
       grid: {
        bottom: '5%', // 设置底边距
        containLabel: true // 是否包含坐标轴标签
    },
    legend: {
        icon: 'rect',
        itemWidth: 10,
        itemHeight: 4,
        itemGap: 24,
        data: ['AI前', 'AI后'],
        textStyle: {
            color: '#c1dafc',
            fontSize: '12'
        },
        right: '30%'
    },
     xAxis: {
            type: 'category',
            name: '料号名',
            data: jobname,
            axisLabel: {
                rotate: 45, // 将标签旋转45度
                show: true,
                textStyle: {
                    color: '#333',

                }
            }
        },
    yAxis: [
        {
            type: 'value',
            name: '平均报点：',
            axisLabel: {
                formatter: '{value}'
            }
        }
    ],
    series: [
        {
            name: 'AI前',
            type: 'bar',
            barWidth: '10%',
            data: fJObMeanAll,
            itemStyle: {
                color: '#b1de6a' // 单独设置数据系列的颜色
            },
            label: {
                show: true, // 显示标签
                position: 'top', // 标签位置：顶部
                formatter: '{c}', // 标签内容格式
                color: '#333' // 标签文字颜色
            }
        },
        {
            name: 'AI后',
            type: 'bar',
            barWidth: '10%',
            data: fJObMeanAi,
            itemStyle: {
                color: '#4ab0ee' // 单独设置数据系列的颜色
            },
            label: {
                show: true, // 显示标签
                position: 'top', // 标签位置：顶部
                formatter: '{c}', // 标签内容格式
                color: '#333' // 标签文字颜色
            }
        }
    ],
    dataZoom: [
        {
            type: 'slider', // 设置为滑动条类型
            show: false
        },
        {
            type: 'inside', // 设置为内部滑动条类型
            start: 0, // 数据窗口的起始位置百分比
            end: 100, // 数据窗口的结束位置百分比
            filterMode: 'filter' // 设置为过滤模式，即在缩放时过滤数据
        }
    ],
};
    myChart.setOption(option);
    window.addEventListener("resize", (event) => {
        myChart.resize()
    });
}

function generateJobAi(jobnameData,fJobAiData){
    var myChart = echarts.init($("#container6")[0]);
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['假点过滤率'],
            textStyle: {
                color: '#333'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            name: '料号名',
            data: jobnameData,
            axisLabel: {
                rotate: 45, // 将标签旋转45度
                show: true,
                textStyle: {
                    color: '#333',

                }
            }
        },
        yAxis: [
            {
                type: 'value',
                name: '假点过滤率',
                max: 100,  // 设置最大值为 100
                interval: 10,
                axisLabel: {
                    show: true,
                    formatter: '{value}%'
                },
            }
        ],
        dataZoom: [
            {
                type: 'slider',  // 设置为滑动条类型
                show: false
            },
            {
                type: 'inside',  // 设置为内部滑动条类型
                start: 0,  // 数据窗口的起始位置百分比
                end: 100,   // 数据窗口的结束位置百分比
                filterMode: 'filter'  // 设置为过滤模式，即在缩放时过滤数据
            }
        ],
        series: [
            {
                name: '假点过滤率',
                type: 'line',
                max: 100,
                data: fJobAiData,
                itemStyle: {
                    color: '#b1de6a'
                },
                label: {
                    show: true,
                    formatter: '{c}%' // 显示百分比
                },
                toolbox: {
                    feature: {
                        dataZoom: {  // 数据区域缩放工具
                            yAxisIndex: false  // 不允许对纵坐标轴进行缩放
                        },
                        dataView: {  // 数据视图工具
                            readOnly: true  // 设置为只读，用户无法编辑数据视图
                        },
                        magicType: {  // 图表类型切换工具
                            type: ['line', 'bar']  // 设置支持切换的图表类型
                        },
                        restore: {},  // 还原工具
                        saveAsImage: {}  // 保存为图片工具
                    }
                },
            }
        ]
    };
    myChart.setOption(option);
    window.addEventListener("resize", (event) => {
        myChart.resize()
    });
}

 function generateJobErr(errJobtypedata, errJobNumData, errJobRateData, errAllNum, errPlnoNameData) {
    console.log(errAllNum);
    var myChart = echarts.init($("#container7")[0]);
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['数量', '占比'],
            textStyle: {
                color: '#333'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
         xAxis: {
            type: 'category',
            name: '缺陷名',
            data: errJobtypedata,
            axisLabel: {
                rotate: 45, // 将标签旋转45度
                show: true,
                textStyle: {
                    color: '#333',

                }
            }
        },
        yAxis: [
            {
                type: 'value',
                name: '数量',
                max :errAllNum,
                axisLabel: {
                    show: true,
                    textStyle: {
                        color: '#333'
                    }
                }
            },
            {
                type: 'value',
                name: '占比',
                max: 100,  // 设置最大值为 100
                interval: 10,
                axisLabel: {
                    show: true,
                    formatter: '{value}%'
                }
            }
        ],
        dataZoom: [
            {
                type: 'slider',  // 设置为滑动条类型
                show: false
            },
            {
                type: 'inside',  // 设置为内部滑动条类型
                start: 0,  // 数据窗口的起始位置百分比
                end: 100,   // 数据窗口的结束位置百分比
                filterMode: 'filter'  // 设置为过滤模式，即在缩放时过滤数据
            }
        ],
        series: [
            {
                name: '数量',
                type: 'bar',
                barWidth: '10%',
                data: errJobNumData,
                itemStyle: {
                    color: '#4ab0ee'
                }
            },
            {
                name: '占比',
                type: 'line',
                yAxisIndex: 1, // 使用第二个 y 轴
                data: errJobRateData,
                itemStyle: {
                    color: '#b1de6a'
                },
                label: {
                    show: true,
                    formatter: '{c}%' // 显示百分比
                }
            }
        ]
    };
    myChart.setOption(option);
    window.addEventListener("resize", (event) => {
        myChart.resize()
    });

        // 添加导出按钮点击事件
    $('#exportButton').off('click').click(function() {
        exportToCSV(errJobtypedata, errJobNumData, errJobRateData, errPlnoNameData);
    });
}
// 导出为 CSV 的函数
function exportToCSV(types, numbers, rates, errPlnoNameData) {
    var csvContent = "\uFEFF";
    csvContent += "缺陷名,数量,占比\n"; // CSV header

    for (var i = 0; i < types.length; i++) {
        csvContent += types[i] + "," + numbers[i] + "," + rates[i] + "%\n";
    }

    // 创建一个隐藏的下载链接
    var encodedUri = encodeURI("data:text/csv;charset=utf-8," + csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", errPlnoNameData + "_" + "ErrTypeData.csv");
    document.body.appendChild(link); // 需要将链接加入到 DOM 中才能点击

    link.click();
    document.body.removeChild(link); // 点击后移除该链接
}

 function generatePlnoErr(errPlnotypedata, errPlnoNumData, errPlnoRateData,errPlnoAllNum) {
    var myChart = echarts.init($("#container8")[0]);
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['数量', '占比'],
            textStyle: {
                color: '#333'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
         xAxis: {
            type: 'category',
            name: '缺陷名',
            data: errPlnotypedata,
            axisLabel: {
                rotate: 45, // 将标签旋转45度
                show: true,
                textStyle: {
                    color: '#333',

                }
            }
        },
        yAxis: [
            {
                type: 'value',
                name: '数量',
                max :errPlnoAllNum,
                axisLabel: {
                    show: true,
                    textStyle: {
                        color: '#333'
                    }
                }
            },
            {
                type: 'value',
                name: '占比',
                max: 100,  // 设置最大值为 100
                interval: 10,
                axisLabel: {
                    show: true,
                    formatter: '{value}%'
                }
            }
        ],
        dataZoom: [
            {
                type: 'slider',  // 设置为滑动条类型
                show: false
            },
            {
                type: 'inside',  // 设置为内部滑动条类型
                start: 0,  // 数据窗口的起始位置百分比
                end: 100,   // 数据窗口的结束位置百分比
                filterMode: 'filter'  // 设置为过滤模式，即在缩放时过滤数据
            }
        ],
        series: [
            {
                name: '数量',
                type: 'bar',
                barWidth: '10%',
                data: errPlnoNumData,
                itemStyle: {
                    color: '#4ab0ee'
                }
            },
            {
                name: '占比',
                type: 'line',
                yAxisIndex: 1, // 使用第二个 y 轴
                data: errPlnoRateData,
                itemStyle: {
                    color: '#b1de6a'
                },
                label: {
                    show: true,
                    formatter: '{c}%' // 显示百分比
                }
            }
        ]
    };
    myChart.setOption(option);
    window.addEventListener("resize", (event) => {
        myChart.resize()
    });
}

