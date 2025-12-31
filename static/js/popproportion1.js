async function calculate_ci_oneprop() {

    const sample_size = parseInt(
        document.getElementById("sample_size1").value
    );

    const proportion = parseFloat(
        document.getElementById("sample_prop1").value
    );

    const alpha = parseFloat(
        document.getElementById("alpha1").value
    );

    const formData = new FormData();
    formData.append("sample_size", sample_size);
    formData.append("proportion", proportion);
    formData.append("alpha", alpha);

    const res = await fetch("/populationproportion/calculate_ci_proportion1", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    if (data.CI) {
        const el = document.getElementById("ci-result-proportion1");
        el.innerHTML = `
        CI = (${data.CI[0]},  ${data.CI[1]}) <br>
        ME = ${data.ME} <br>
        Critical Value = 
        \\(z_{\\alpha/2} \\) = ${data.z_alpha} <br>
        
        `;
        el.style.fontSize = "25px";
        el.style.textAlign = "center";
        el.style.fontWeight = "bold";
        MathJax.typesetPromise([el]);
        
    }
    if (data.image) {
        document.getElementById("proportion1-plot").src = "data:image/png;base64," + data.image;
    }
}













async function calculate_ht_oneprop() {
    const sample_size = parseInt(
        document.getElementById("sample_size_ht1").value
    );
    const proportion = parseFloat(
        document.getElementById("sample_prop_ht1").value
    );
    const null_prop = parseFloat(
        document.getElementById("null_prop_ht1").value
    );
    const alpha = parseFloat(
        document.getElementById("alpha_ht1").value
    );
    const test_type = document.getElementById("test_type").value;
    const formData = new FormData();
    formData.append("sample_size", sample_size);
    formData.append("sample_proportion", proportion);
    formData.append("null_prop", null_prop);
    formData.append("alpha", alpha);
    formData.append("test_type", test_type);
    const res = await fetch("/populationproportion/proportion1_ht", {
        method: "POST",
        body: formData
    }); 
    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }   
    if (data.z) {
        const el = document.getElementById("proportion-ht1-result");
        el.innerHTML = `
        Test Statistic (z) = ${data.z} <br>
        Critical Value (z) = ${data.z_alpha} <br>
        P-value = ${data.p_value} <br>  
        \\( \\alpha\\) = ${data.alpha}
        `;
        el.style.fontSize = "25px";
        el.style.textAlign = "center";
        el.style.fontWeight = "bold";
        MathJax.typesetPromise([el]);
    }
    if (data.image) {
        document.getElementById("proportion-ht1-plot").src = "data:image/png;base64," + data.image;
    }
}
    