import streamlit as st
import numpy as np
import pandas as pd

# import sklearn


import pdfplumber

st.title("PDF Grade Calculator")
# st.text("This is a quick website to calculate your average grade. \nIt's not difficult to do manually, but it's tedious work!")
# st.text("The official reciepe to calculate grades can be found at ")
st.markdown("This website calculates the average grade from any Vitnemålsportalen grade transcript PDF, so you don't have to do it by hand:)" )


# st.markdown("The official reciepe to calculate grades can be found at ")
st.header("How to use")
st.markdown(
    "The PDF format required is the one from [vitnemålsportalen](%s)."
    % "https://www.vitnemalsportalen.no/"
)
st.markdown(
    "*Do not use the grade preview!* The correct way to get the PDF from vitnemålsportalen is the following: "
)
st.markdown(
    """
    * Log in, and click on my results, 
    * Select the courses you want to calculate the average of,
    * Click next **twice** (do not download the preview here!), 
    * Fill in your email, and select norwegian/english (both are fine), then click next
    * Click on the link sent to your email 
    * Scroll past all your grades to the bottom, then download the PDF
    """
)

uploaded_file = st.file_uploader("Upload your pdf file here")

if uploaded_file:
    # extract text info
    with pdfplumber.open(uploaded_file) as pdf:
        text_data = ""
        for page in pdf.pages:
            text_data += page.extract_text()
    # df to be filled in later
    columns = ["Course code", "Letter grade", "Number grade", "Course credits"]
    df = pd.DataFrame(columns=columns)

    lines = text_data.split("\n")
    for line in lines:
        # NTNU courses either have two or three upper case letters, such as TMA4100 og FY1001.
        # This filters out the random text in the transcript
        # Not super robust, but it works
        if (line[0:2].isalpha()) and (line[0:2].isupper()):
            words = line.split()
            code = words[0]
            letter_grade = words[-1]
            course_credits = words[-3]

            # This handles weird courses with 0 credits such as HMS0001
            if len(course_credits) > 3:
                course_credits = np.nan

            # Convert letter grades to numbers.
            if len(letter_grade) == 1:
                grade = 70 - ord(letter_grade)  # A capital F has ASCII value 70

            # This handles the "passed" grade.
            else:
                grade = np.nan

            # Add course info to the dataframe
            df.loc[df.shape[0]] = [code, letter_grade, grade, course_credits]
    # We must convert the credits from 7,5 to 7.5

    course_credits_values = np.array(df["Course credits"].values)

    # ugly, but does the job
    for i in range(len(course_credits_values)):
        course_credits_values[i] = float(
            str(course_credits_values[i]).replace(",", ".")
        )
    df["course_values"] = course_credits_values

    # We have to ignore the course credits corresponding to course without letter grade when calculating a weighted average
    Total_credits_in_courses_with_grade = (
        df["course_values"].sum() - df[df["Number grade"].isna()]["course_values"].sum()
    )

    # Calculate weighted average. This is done by multiplying the grade by the credits, dividing by all the relevant credits.
    # Note that pandas df will automatically consider NaNs as 0 when summing, which makes the numerator nice.
    # The reason why the denominator needs the ugly solution is because there exist courses with credits and no grade, which are not removed by being multiplied by a nan (such as in the denominator)
    avg_grade = (df["course_values"] * df["Number grade"]).sum() / (
        Total_credits_in_courses_with_grade
    )

    st.markdown(f" ### Average grade: {avg_grade:.2f}")

    st.markdown(
        f"Your course credit weighted average grade is {avg_grade:.2f}. This is the one you report."
    )

    unweighted_average = df["Number grade"].mean()
    st.markdown(
        f"Your unweighted average grade is {unweighted_average:.2f}. This number should not be presented as your average grade, as it's just the average of all your grades, regardless of how many credits the course gives. If all your courses are 7.5 credits, the number is identical."
    )
    st.header("Verifying your results")
    st.markdown(
        "To be sure that the results are reliable, you can check that the PDF was parsed correctly. The following dataframe was extracted from the uploaded PDF."
    )
    st.markdown(
        f"* Check that you have **{df.shape[0]}** courses on your original transcript"
    )
    st.markdown(
        '* Verify that any pass/fail courses have been converted to "None" in the Grade column'
    )
    st.markdown("* Verify that the course credits are correct")
    st.markdown(
        "* Check that unusual courses such as HMS0001 has no credits and no grade"
    )
    st.dataframe(
        df[["Course code", "Letter grade", "Number grade", "Course credits"]],
        800,
        1500,
        hide_index=True,
    )

# st.markdown("If you liked this page and want to say thanks, my Vipps is 41303423 :)")


st.markdown(
    """
            This page was originally made for NTNU transcripts. It appears to work for other universities as well, but the PDF parsing has not been tested thoroughly.
            If you find any issues, please send an email to gradecalculatorntnu@gmail.com
            """
)

st.markdown(
    "NTNU's official procedure for grade calculations can be found [here](%s). When applying to master's degrees, only one decimal is used. This page calculates two decimals for convenience."
    % "https://i.ntnu.no/wiki/-/wiki/Norsk/FS+-+Beregne+snittkarakter"
)

