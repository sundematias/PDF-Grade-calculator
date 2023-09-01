import streamlit as st
import numpy as np
import pandas as pd
import pdfplumber

st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-bottom: 4rem;
                    padding-left: 1.8rem;
                    padding-right: 1.8rem;
                }
        </style>
        """, unsafe_allow_html=True)


st.title("PDF Grade Calculator")
st.markdown("This website calculates the average grade from any Vitnemålsportalen grade transcript PDF, so you don't have to do it by hand:)" )

st.header("How to use")
st.markdown(
    "The PDF format required is from [Vitnemålsportalen](%s). *Do not use the grade preview, but the proper PDF!*"
    % "https://www.vitnemalsportalen.no/"
)
st.markdown(
    " The correct way to get the PDF from vitnemålsportalen: "
)
st.markdown(
    """
    * Log in, and click on my results, 
    * Select the courses you want to calculate the average of
    * Click next **twice** (do not download the preview here!)
    * Fill in your email, and select language (any language works), then click next
    * Click on the link sent to your email 
    * Scroll past all your grades to the bottom, then download the PDF
    """
)

uploaded_file = st.file_uploader("Upload your pdf file here")

if uploaded_file:
    try:
            
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
                # st.markdown(words)
                
                #these three lines make more sense if you print the "words" variable
                code = words[0]
                letter_grade = words[-1]
                course_credits = words[-3]


                def num_there(s):
                    return any(i.isdigit() for i in s)
                # This handles weird courses with 0 credits such as HMS0001
                if (len(course_credits) > 3) or (not num_there(course_credits)):
                    course_credits = np.nan
                
                #duplicate courses where the second has zero credits behaves differently
                # if course_credits == '—':
                #     course_credits = np.nan
                
                
                # if not num_there(course_credits):
                #     course_credits = np.nan
                
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
        # st.markdown(course_credits_values)
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
        unweighted_average = df["Number grade"].mean()
        
        st.header("Verifying the number")
        st.markdown(
            "To be sure that the average is correct, you can do some checks to verify that the PDF was parsed correctly:"
        )
        st.markdown(
            f"* Check that you have **{df.shape[0]}** courses on your original transcript"
        )
        st.markdown(
            '* Verify that any pass/fail courses have been converted to "None" in the Number Grade column'
        )
        st.markdown("* Verify that the course credits are correct")
        st.markdown(
            "* Check that unusual courses such as HMS0001 has no credits and no grade"
        )
        st.dataframe(
            df[["Course code", "Letter grade", "Number grade", "Course credits"]],
            800,
            200,
            hide_index=True,
        )
        st.markdown("*Hover over the data to get a fullscreen button*")
        st.text("")
    except:
        st.markdown(" **:red[An error occured.]** \nMake sure the PDF is correctly formatted. There could also be some edge case un your PDF that is not handled yet. Contact gradecalculatorntnu@gmail.com to report any bugs.")


#st.header("About")
# st.markdown("""---""") 
# st.divider()
st.write('***')

st.markdown(
    """
            This page was originally made for NTNU transcripts. It appears to work for other universities as well, but the PDF parsing has not been tested thoroughly.
            If you find any issues, please send an email to gradecalculatorntnu@gmail.com
            """
)

st.markdown(
    "NTNU's official procedure for grade calculations can be found [here](%s). When applying to master's degrees, only one decimal is used. This page calculates two decimals for convenience. The average is weighted by course credits."
    % "https://i.ntnu.no/wiki/-/wiki/Norsk/FS+-+Beregne+snittkarakter"
)

st.markdown("This page is not affiliated with NTNU or Vitnemålsportalen. The source code is available on [GitHub](%s). " % "https://github.com/sundematias/sundematias.github.io")

