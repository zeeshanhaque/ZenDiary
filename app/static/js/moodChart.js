document.addEventListener('DOMContentLoaded', function () {
    if (typeof window.moodValues !== 'undefined' && typeof window.timeCategories !== 'undefined') {
        var moodData = {
            chart: {
                type: 'line',
                height: 360,
                width: 1080,
            },
            series: [{
                name: 'Mood',
                data: window.moodValues
            }],
            xaxis: {
                categories: window.timeCategories,
                labels: {
                    style: {
                        fontFamily: 'Mukta'
                    }
                }
            },
            yaxis: {
                labels: {
                    formatter: function (value) {
                        switch (value) {
                            case 1:
                                return '😢';
                            case 2:
                                return '😐';
                            case 3:
                                return '😊';
                            case 4:
                                return '😄';
                            case 5:
                                return '😍';
                            default:
                                return '';
                        }
                    }
                },
                tickAmount: 5
            },
            stroke: {
                curve: 'smooth',
                colors: ['#2BAE66']
            },
            tooltip: {
                enabled: true
            }
        };
        var moodChart = new ApexCharts(document.querySelector("#moodChart"), moodData);
        moodChart.render();
    } else {
        console.error("Chart data not found");
    }
});