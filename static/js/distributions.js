async function addCurve() {
    const mean = document.getElementById("mean").value;
    const std = document.getElementById("std").value;

    const formData = new FormData();
    formData.append("mean", mean);
    formData.append("std", std);

    const res = await fetch("/distributions/add_curve", {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    document.getElementById("plot").src = "data:image/png;base64," + data.img;
}

async function resetPlot() {
    const res = await fetch("/distributions/reset", {
        method: "POST"
    });

    const data = await res.json();
    document.getElementById("plot").src = "data:image/png;base64," + data.img;
}





async function pz_value() {
    const z_value = document.getElementById("z-value").value;
    const p_value = document.getElementById("p-value").value;
    const formData = new FormData();
    formData.append("z_given", z_value);
    formData.append("p_given", p_value);
    const res = await fetch("/distributions/zdistribution", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
    } else {
       
        // Update text (do NOT delete the img)
    document.getElementById("zp-results").innerHTML = data.dataframe + 
    `<br><img id="zp-plot" src="data:image/png;base64,${data.plot_path}" style="width:600px; border-radius: 10px; border:1px solid #ccc;">`;
        
    }
}




async function calculateTDistribution() {
    const t_score = document.getElementById("t-score").value;
    const df = document.getElementById("df").value;
    const p_value = document.getElementById("p-value").value;

    const formData = new FormData();
    formData.append("t_given", t_score);
    formData.append("df_given", df);
    formData.append("p_given", p_value);

    const res = await fetch("/distributions/tdistribution", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    const resultsDiv = document.getElementById("tp-results");
    resultsDiv.innerHTML = "";  // Clear old results

    // === Show error ===
    if (data.error) {
        resultsDiv.innerHTML = `<p style="color: red; font-weight: bold;">${data.error}</p>`;
        return;
    }

    // === Insert dataframe (if exists) ===
    if (data.dataframe) {
        resultsDiv.insertAdjacentHTML("beforeend", data.dataframe);
    }

    // === Insert the plot (if exists) ===
    if (data.plot_path) {
        resultsDiv.insertAdjacentHTML(
            "beforeend",
            `<br><img id="tp-plot" 
              src="data:image/png;base64,${data.plot_path}"
              style="width:600px; border-radius:10px; border:1px solid #ccc; margin-top:15px;">`
        );
    }
}



//**************************************************************************************************************************

async function calculateChiSquareDistribution() {

    const chi2_score = document.getElementById("chi2-score").value;
    const df = document.getElementById("df").value;
    const p_value = document.getElementById("p-value").value;
    const formData = new FormData();
    formData.append("chi2_given", chi2_score);
    formData.append("df_given", df);
    formData.append("p_given", p_value);
    const res = await fetch("/distributions/chisquaredistribution", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    const resultsDiv = document.getElementById("chi2-results");
    resultsDiv.innerHTML = "";  // Clear old results
    // === Show error ===
    if (data.error) {
        resultsDiv.innerHTML = `<p style="color: red; font-weight: bold;">${data.error}</p>`;
        return;
    }
    // === Insert dataframe (if exists) ===
    if (data.dataframe) {
        resultsDiv.insertAdjacentHTML("beforeend", data.dataframe);
    }
    // === Insert the plot (if exists) ===
    if (data.plot_path) {
        resultsDiv.insertAdjacentHTML(
            "beforeend",
            `<br><img id="chi2-plot" 
              src="data:image/png;base64,${data.plot_path}"
              style="width:600px; border-radius:10px; border:1px solid #ccc; margin-top:15px;">`
        );
    }
}   


async function drawChiSquareDistribution() {
    const df = document.getElementById("df_plot").value;
    const formData = new FormData();
    formData.append("df", df);
    const res = await fetch("/distributions/add_chisquare_curve", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.img) {
        document.getElementById("plot").src = "data:image/png;base64," + data.img;
    }
}

async function reset1() {
    const res = await fetch("/distributions/reset_chisquare", {
        method: "POST"
    });
    const data = await res.json();
    document.getElementById("plot").src = "data:image/png;base64," + data.img;
}





//**************************************************************************************************************************
// F-distribution functions

async function drawFDistribution() {
    const dfn = document.getElementById("df1_plot").value;
    const dfd = document.getElementById("df2_plot").value;
    const formData = new FormData();
    formData.append("dfn", dfn);
    formData.append("dfd", dfd);
    const res = await fetch("/distributions/add_f_curve", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    if (data.img) {
        document.getElementById("f-plot").src = "data:image/png;base64," + data.img;
    }
}


async function resetFPlot() {
    const res = await fetch("/distributions/reset_f", {
        method: "POST"
    });
    const data = await res.json();
    document.getElementById("f-plot").src = "data:image/png;base64," + data.img;
}



async function calculateFDistribution() {
    const f_score = document.getElementById("fscore_input").value;
    const dfn = document.getElementById("df1_input").value;
    const dfd = document.getElementById("df2_input").value;
    const p_value = document.getElementById("pvalue_input").value;   
    const formData = new FormData();
    formData.append("f_given", f_score);
    formData.append("dfn_given", dfn);
    formData.append("dfd_given", dfd);
    formData.append("p_given", p_value);
    const res = await fetch("/distributions/fdistribution", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    const resultsDiv = document.getElementById("f-results");
    resultsDiv.innerHTML = "";  // Clear old results
    // === Show error ===
    if (data.error) {
        resultsDiv.innerHTML = `<p style="color: red; font-weight: bold;">${data.error}</p>`;
        return;
    }
    // === Insert dataframe (if exists) ===
    if (data.dataframe) {
        resultsDiv.insertAdjacentHTML("beforeend", data.dataframe);
    }
    // === Insert the plot (if exists) ===
    if (data.img) {
        resultsDiv.insertAdjacentHTML(
            "beforeend",
            `<br><img id="f-plot" 
              src="data:image/png;base64,${data.img}"
              style="width:600px; border-radius:10px; border:1px solid #ccc; margin-top:15px;">`
        );
    }
}   
