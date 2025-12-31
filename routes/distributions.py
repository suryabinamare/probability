import base64

import io
from flask import Flask, request, Blueprint, render_template, current_app, jsonify
import os
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f
from scipy.stats import norm
from scipy.stats import t
from scipy.stats import chi2
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend






distributions_bp = Blueprint("distributions", __name__, template_folder="../templates")

curves = []

def generage_plot():
    for mean, std in curves:
        x = np.linspace(mean - 4*std, mean + 4*std, 400)
        y = (1/(std * np.sqrt(2*np.pi))) * np.exp(-((x-mean)**2) / (2*std**2))
        plt.plot(x, y, label=f"μ={mean}, σ={std}")
        y1 = np.zeros(len(x))
        plt.plot(x, y1, color='black')  # x-axis
        plt.plot(mean, 0, 'ro')  # mean point
        plt.axvline(mean, color='red', linestyle='--')
    plt.title("Normal Distributions")

    plt.legend()
    plt.grid()
    # Save plot to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return encoded





@distributions_bp.route("/zdistribution", methods=["GET", "POST"])
def zdistribution():
    if request.method == "GET":
        # Simply render the HTML page when the user opens /distributions/zdistribution
        return render_template("z-distribution.html")
    # Initialize values so they always exist
    z_value = None
    p_value = None
    error = None
    encoded = None
    df = None
    try:
        # Read raw input (string)
        raw_z = request.form.get("z_given", "").strip()
        raw_p = request.form.get("p_given", "").strip()


        # Determine which one was provided
        has_z = raw_z != ""
        has_p = raw_p != ""

        if has_z:
            # Convert to float
            z_value = float(raw_z)
            p_value = norm.cdf(z_value)

        elif has_p:
            p_value = float(raw_p)
            if 0 < p_value < 1:
                z_value = norm.ppf(p_value)
            else:
                error = "P-value must be between 0 and 1 (exclusive)."
        else:
            error = "Please provide either a Z-score or a P-value."
        df = pd.DataFrame({"Z-Value": [z_value], "P-Value": [p_value]})
        df = df.reset_index(drop=True)

        # === Generate Plot ===
        if z_value is not None and error is None:
            x = np.linspace(-3, 3, 500)
            y = norm.pdf(x)
            y1 = np.zeros(len(x))

            fig, ax = plt.subplots()
            ax.plot(x, y, label='Normal Distribution')

            # Z score marker
            ax.plot(z_value, 0, 'ro', label='Z-score')
            ax.plot(x, y1, color='black')  # x-axis
            ax.axvline(z_value, color='red', linestyle='--')

            # Fill area under curve
            x_fill = np.linspace(-3, z_value, 500)
            y_fill = norm.pdf(x_fill)
            ax.fill_between(x_fill, y_fill, alpha=0.6, color='skyblue', label='P-value')

            ax.text(z_value-0.1, 0.05, f"P = {p_value:.4f}", color="red", ha="right")
            ax.set_xlabel("Z-value")
            ax.set_ylabel("Density")
            ax.legend()

            # Save figure to base64
            buf1 = io.BytesIO()
            plt.savefig(buf1, format="png")
            buf1.seek(0)
            encoded = base64.b64encode(buf1.read()).decode("utf-8")
            plt.close()

    except Exception as e:
        error = f"Error: {str(e)}"

    return jsonify({
        "z_value": z_value,
        "p_value": p_value,
        "dataframe": df.to_html(classes="fancy-table") if df is not None else None,
        "plot_path": encoded,
        "error": error
    })


@distributions_bp.route("/add_curve", methods = ['GET', 'POST'])
def add_curve():
    mean = float(request.form["mean"])
    std = float(request.form["std"])
    try:
        if std <= 0:
            return jsonify({"error": "Standard deviation must be positive."}), 400
        curves.append((mean, std))

        image = generage_plot()
    except ValueError:
        return jsonify({"error": "Invalid input for mean or standard deviation."}), 400    
    return jsonify({"img": image})




@distributions_bp.route("/reset", methods = ['GET', 'POST'])
def reset():
    curves.clear()
    image = generage_plot() 
    return jsonify({"img": image})


#*****************************************************************************************************************************

# Chi-Square Distribution

chisquare_curves = []
def generate_chisquare_plot():
    for df in chisquare_curves:
        x = np.linspace(0, 3*df, 500)
        y = chi2.pdf(x, df)
        plt.plot(x, y, label=f"df={df}")
        y1 = np.zeros(len(x))
        x1 = np.zeros(len(x))
        plt.plot(x, y1, color='black')  # x-axis
        plt.plot(x1, y, color='black')  # y-axis
        plt.plot(df, 0, 'ro')  # mean point
        plt.axvline(df, color='red', linestyle='--')
        
    plt.title("Chi-Square Distributions")

    plt.legend()
    #plt.grid()
    # Save plot to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return encoded
@distributions_bp.route("/add_chisquare_curve", methods = ['GET', 'POST'])
def add_chisquare_curve():
    error = None
    df = float(request.form["df"])
    try:
        if df <= 0:
            return jsonify({"error": "Degrees of Freedom must be positive."}), 400
        chisquare_curves.append((df))

        image = generate_chisquare_plot()
    except ValueError:
        return jsonify({"error": "Invalid input for Degrees of Freedom."}), 400    
    return jsonify({"img": image, "error": error})



@distributions_bp.route("/reset_chisquare", methods=["POST", "GET"])
def reset_chisquare():
    chisquare_curves.clear()
    image = generate_chisquare_plot()
    return jsonify({"img": image})






@distributions_bp.route("/chisquaredistribution", methods=["GET", "POST"])
def chisquaredistribution():
    chisquare = None
    p_value = None
    encoded = None
    df = None
    error = None

    if request.method == "GET":
        return render_template("chisquare_distribution.html")

    try:
        chi_raw = request.form.get("chi2_given")
        df_raw = request.form.get("df_given")
        p_raw = request.form.get("p_given")   # rename in HTML too

        # ---------- Validate df ----------
        if not df_raw or not df_raw.isdigit():
            return jsonify({"error": "Degrees of Freedom must be a positive integer."})

        df_input = int(df_raw)

        # ---------- Case 1: chi-square + df ----------
        if chi_raw not in (None, ""):
            chisquare = float(chi_raw)
            p_value = chi2.sf(chisquare, df_input)

        # ---------- Case 2: p-value + df ----------
        elif p_raw not in (None, ""):
            p_value = float(p_raw)
            if not (0 < p_value < 1):
                return jsonify({"error": "P-value must be between 0 and 1."})
            chisquare = chi2.isf(p_value, df_input)

        else:
            return jsonify({"error": "Provide either (chi2 + df) OR (p-value + df)."})

        # ---------- Build DataFrame ----------
        df = pd.DataFrame({
            "Chi-Square Value": [chisquare],
            "Degrees of Freedom": [df_input],
            "P-Value": [p_value]
        })

        # ---------- Plot ----------
        x = np.linspace(0, 4*df_input, 500)
        y = chi2.pdf(x, df_input)
        y1 = np.zeros(len(x))
        x1 = np.zeros(len(x))

        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(x, y, label='Chi-Square Distribution')
        ax.plot(x1, y, color='black')  # y-axis
        ax.plot(x, y1, color='black')  # x-axis
        ax.plot(chisquare, 0, 'ro', label = "Chi-Square Value")  # chi-square point
        ax.axvline(chisquare, color="red", linestyle="--")
        ax.fill_between(x[x >= chisquare], y[x >= chisquare], alpha=0.6, color='skyblue', label='P-Value Area')
        ax.text(chisquare + 0.1, 0.01, f'p-value = {p_value:.4f}', color='red', ha='left')
        ax.set_xlabel("Chi-Square Value")
        ax.set_ylabel("Probability Density")
        ax.legend()

        # Save to base64
        buf1 = io.BytesIO()
        plt.savefig(buf1, format="png")
        buf1.seek(0)
        encoded = base64.b64encode(buf1.read()).decode()
        plt.close(fig)

    except Exception as e:
        error = f"Error: {str(e)}"

    return jsonify({
        "dataframe": df.to_html(classes="fancy-table") if df is not None else None,
        "plot_path": encoded,
        "error": error
    })





#*****************************************************************************************************************************

# T-distribution
@distributions_bp.route("/tdistribution", methods=["GET", "POST"])

def tdistribution():
    if request.method == 'GET':
        return render_template('t-distribution.html')
    t_value = None
    p_value = None
    df_input = None
    encoded = None
    df = None
    error = None

    
    try:
        # Get form inputs
        t_input = request.form.get('t_given')
        df_input = float(request.form.get('df_given'))
        p_input = request.form.get('p_given')

        if t_input and df_input:
            if int(df_input):
                t_value = float(t_input)
                p_value = t.cdf(t_value, df_input)
            else:
                error = "Degree of Freedom should be positive integer."

        elif p_input and df_input:
            p_value = float(p_input)
            if 0 < p_value < 1:
                if int(df_input)>0:
                    t_value = t.ppf(p_value, df_input)
                else:
                    error = "Degree of Freedom should be positive integer."
            else:
                error = "P-value must be between 0 and 1 (exclusive)."
        else:
            error = "Please provide either a t-score and df or a P-value and df."
        df = pd.DataFrame({"t-Value": [t_value], "Degrees of Freedom": [df_input], "P-Value": [p_value]})
        df = df.reset_index(drop=True)

        # === Generate Plot if we have a valid t-score ===
        if t_value is not None and error is None:
            x = np.linspace(-3, 3, 500)
            y = t.pdf(x,df_input)
            y1 = np.zeros(len(x))
            fig, ax = plt.subplots(figsize = (8,6))

            ax.plot(x, y, label='t-Distribution')
            ax.plot(t_value, 0, 'ro', label='t-score')
            ax.plot(x, y1, color='black')  # x-axis


            # Fill area under curve up to Z
            x_fill = np.linspace(-3, t_value, 500)
            y_fill = t.pdf(x_fill, df_input)
            ax.fill_between(x_fill, y_fill, color='skyblue', alpha=0.6, label = "P-Value")

            ax.axvline(t_value, color='red', linestyle='--')
            ax.text(t_value - 0.1, 0.05, f'p-value = {p_value:.4f}', color='red', ha='right')
            #ax.set_title('Z-Score and P-Value on Normal Curve')
            ax.set_xlabel('t-value')
            ax.set_ylabel('Probability Density')
            ax.set_xticks([t_value])
            ax.legend()

             # Save figure to base64
            buf1 = io.BytesIO()
            plt.savefig(buf1, format="png")
            buf1.seek(0)
            encoded = base64.b64encode(buf1.read()).decode("utf-8")
            plt.close()

    except Exception as e:
        error = f"Error: {str(e)}"

    return jsonify({"dataframe": df.to_html(classes="fancy-table") if df is not None else None,
                    "plot_path": encoded,
                    "error": error})










#*****************************************************************************************************************************
# F-distribution
dof = []
def generate_f_plot():
    for dfn, dfd in dof:
        mean = f.mean(dfn, dfd)
        std = f.std(dfn, dfd)
        x_max = mean + 3 * std

        x = np.linspace(0, x_max, 500)
        y = f.pdf(x, dfn, dfd)
        plt.plot(x, y, label=f"dfn={dfn}, dfd={dfd}")
        y1 = np.zeros(len(x))
        x1 = np.zeros(len(x))
        plt.plot(x1, y, color='black')  # y-axis
        plt.plot(x, y1, color='black')  # x-axis
        plt.plot(mean, 0, 'ro', label = "Mean")  # mean point
        #plt.axvline(mean, color='red', linestyle='--')
        
    plt.title("F-Distributions")

    plt.legend()
    #plt.grid(True)
    # Save plot to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close('all')
    return encoded

@distributions_bp.route("/add_f_curve", methods = ['GET', 'POST'])
def add_f_curve():
    dfn = float(request.form["dfn"])
    dfd = float(request.form["dfd"])
    error = None
    try:
        if dfn <= 0 or dfd <= 0:
            return jsonify({"error": "Degrees of Freedom must be positive."}), 400
        dof.append((dfn, dfd))


        image = generate_f_plot()
    except ValueError:
        return jsonify({"error": "Invalid input for Degrees of Freedom."}), 400    
    return jsonify({"img": image, "error": error})

@distributions_bp.route("/reset_f", methods=["POST", "GET"])
def reset_f():
    dof.clear()
    image = generate_f_plot()
    return jsonify({"img": image})  









@distributions_bp.route("/fdistribution", methods=["GET", "POST"])
def fdistribution():

    if request.method == "GET":
        return render_template("F-distribution.html")

    df = None
    error = None
    encoded = None

    try:
        f_raw = request.form.get("f_given")
        alpha_raw = request.form.get("p_given")
        dfn_raw = request.form.get("dfn_given")
        dfd_raw = request.form.get("dfd_given")

        # ------------ Validate DF ------------
        if not (dfn_raw and dfn_raw.isdigit() and dfd_raw and dfd_raw.isdigit()):
            return jsonify({"error": "Degrees of freedom must be positive integers."})

        df_num = int(dfn_raw)
        df_deno = int(dfd_raw)

        if df_num < 1 or df_deno < 1:
            return jsonify({"error": "Degrees of freedom must be positive integers."})

        # ------------ CASE 1: alpha → compute F ------------
        if alpha_raw not in (None, ""):
            alpha = float(alpha_raw)
            if not (0 < alpha < 1):
                return jsonify({"error": "P-Value must be between 0 and 1."})

            f_value = f.ppf(1 - alpha, df_num, df_deno)

        # ------------ CASE 2: f-value → compute alpha ------------
        elif f_raw not in (None, ""):
            f_value = float(f_raw)
            if f_value <= 0:
                return jsonify({"error": "F-value must be positive."})

            alpha = 1 - f.cdf(f_value, df_num, df_deno)

        else:
            return jsonify({"error": "Provide either (alpha + df) OR (f-value + df)."})

        # ------------ Create DataFrame ------------
        df = pd.DataFrame({
            "Df (Num)": [df_num],
            "Df (Deno)": [df_deno],
            "P-Value": [alpha],
            "F-Value": [f_value]
        })

        # ------------ Plot ------------
        mean = f.mean(df_num, df_deno)
        std = f.std(df_num, df_deno)
        x_max = mean + 3 * std

        x = np.linspace(0, x_max, 500)
        y = f.pdf(x, df_num, df_deno)
        y1 = np.zeros(len(x))
        x1 = np.zeros(len(x))

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, y, label=f"F-distribution (dfn={df_num}, dfd={df_deno})")
        ax.plot(x1, y, color='black')  # y-axis
        ax.plot(x, y1, color='black')  # x-axis
        ax.plot(f_value, 0, 'ro', label="F-value")  # f-value point
        ax.text(f_value + 0.1, 0.01, f'P-Value = {alpha:.4f}', color='red', ha='left')
        ax.axvline(f_value, color="red", linestyle="--")
        ax.fill_between(x[x >= f_value], y[x >= f_value], alpha=0.4)

        ax.set_title("F-Distribution Curve")
        ax.set_xlabel("F-value")
        ax.set_ylabel("Density")
        ax.legend()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

    except Exception as e:
        error = f"Error: {str(e)}"

    return jsonify({
        "img": encoded,
        "error": error,
        "dataframe": df.to_html(classes="fancy-table") if df is not None else None
    })
