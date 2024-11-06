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
                        if (value === 1) return '😢';
                        if (value === 2) return '😊';
                        if (value === 3) return '😄';
                        if (value === 4) return '😎';
                        if (value === 5) return '🤩';
                        return '';
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
