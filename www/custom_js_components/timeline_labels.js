console.log("timeline_labels.js loaded");

function findPlot() {

    const plot = document.querySelector(".js-plotly-plot");

    if (!plot) {
        setTimeout(findPlot, 500);
        return;
    }

    if (!plot._fullLayout) {
        setTimeout(findPlot, 500);
        return;
    }

    function updateLabels(eventData) {
        let xmin;
        let xmax;

        if (
            eventData["xaxis.range[0]"] !== undefined &&
            eventData["xaxis.range[1]"] !== undefined
        ) {
            xmin = eventData["xaxis.range[0]"];
            xmax = eventData["xaxis.range[1]"];
        }
        else if (eventData["xaxis.range"] !== undefined) {
            xmin = eventData["xaxis.range"][0];
            xmax = eventData["xaxis.range"][1];
        }
        else {
            return;
        }

        const yearsVisible = xmax - xmin;
        const plotWidth = plot._fullLayout.xaxis._length;
        const pixelsPerYear = plotWidth / yearsVisible;

        // plot.data.forEach((trace, idx) => {
        //     console.log(
        //         idx,
        //         trace.mode,
        //         trace.customdata
        //     );
        // });

        const labelTraceIndex = plot.data.length - 1;
        const trace = plot.data[labelTraceIndex];

        const newTexts = [];

        trace.customdata.forEach(row => {

            const name = row[0];
            const minAge = row[1];
            const maxAge = row[2];

            const blobPixels =
                (maxAge - minAge) * pixelsPerYear;

            const maxChars =
                Math.floor(blobPixels / 7);

            let text = "";

            if (maxChars >= 4) {

                if (name.length > maxChars) {
                    text =
                        name.substring(
                            0,
                            maxChars - 3
                        ) + "...";
                }
                else {
                    text = name;
                }

            }

            newTexts.push(text);

        });

        Plotly.restyle(
            plot,
            { text: [newTexts] },
            [labelTraceIndex]
        );

    }
    plot.on('plotly_relayout', function(eventData) {
    console.log(eventData);
    console.log("range =", eventData["xaxis.range"]);
    });

    plot.on("plotly_relayout", updateLabels);

        updateLabels({
            "xaxis.range[0]": plot.layout.xaxis.range[0],
            "xaxis.range[1]": plot.layout.xaxis.range[1]
        });

        // Verberg de volledige labeltrace in de rangeslider
        setTimeout(() => {

            const traces =
                document
                    .querySelector(".rangeplot")
                    ?.querySelectorAll(".trace.scatter");

            if (traces && traces.length > 0) {
                traces[traces.length - 1].style.display = "none";
            }

        }, 1000);
    }

findPlot();