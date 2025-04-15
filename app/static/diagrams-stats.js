window.onload = function() {
    var dataPointsOF = [];
    var dataPointsUF = [];
    var chart1 = new CanvasJS.Chart("Chart1", {
        animationEnabled: true,
        title: {
            text: "Available Questions",
            fontFamily: "-apple-system, system-ui, BlinkMacSystemFont, Segoe UI, Roboto, Ubuntu, Helvetica Neue, sans-serif",
            fontWeight: "normal"
        },
        data: [{
            type: "pie",
            startAngle: 240,
            radius: 100,
            yValueFormatString: "##0.00\"%\"",
            indexLabel: "{label} {y}",
            dataPoints: dataPointsOF
        }]
    });
    var chart2 = new CanvasJS.Chart("Chart2", {
        animationEnabled: true,
        title: {
            text: "Users Choice",
            fontFamily: "-apple-system, system-ui, BlinkMacSystemFont, Segoe UI, Roboto, Ubuntu, Helvetica Neue, sans-serif",
            fontWeight: "normal"
        },
        data: [{
            type: "pie",
            startAngle: 240,
            radius: 100,
            yValueFormatString: "##0.00\"%\"",
            indexLabel: "{label} {y}",
            dataPoints: dataPointsUF
        }]
    });

    function addDataOF(data) {
        for (var i = 0; i < data.length; i++) {
            dataPointsOF.push({
                label: data[i].topic,
                y: data[i].percent
            });
        }
        chart1.render();
        removeLink();
    }

    function addDataUF(data) {
        for (var i = 0; i < data.length; i++) {
            dataPointsUF.push({
                label: data[i].topic,
                y: data[i].percent
            });
        }
        chart2.render();
        removeLink();
    }

    $.json("/diagram-api?topic=true").then(function(response) {
        addDataOF(response);
    })
    $.json("/diagram-api?users=true").then(function(response) {
        addDataUF(response);
    })
    
    function removeLink() {
        let l = document.getElementsByClassName('canvasjs-chart-credit')
        for (i of l) {
            i.remove();
        }
    }
    window.addEventListener("resize", removeLink)
}
