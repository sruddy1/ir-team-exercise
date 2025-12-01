import pandas as pd
from ir_pell_accepts.helper import calc_academic_year_from_term, construct_cohort
from ir_pell_accepts.checks import validate_pell_columns, validate_cohort_columns, validate_enrollment_columns

def grs_cohort_pell(
    dfp: pd.DataFrame,
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    aid_year_column: str = "AID_YEAR",
    cohort_column: str = "Cohort Name",
) -> int:
    """
    Calculate the number of Pell recipients for the given aid year and cohort type.

    Parameters
    ----------
    dfp : pandas.DataFrame
        Pell awards dataframe.
    dfr : pandas.DataFrame
        Retention / cohort dataframe.
    id_column : str
        Column to use for student IDs; must exist in both dataframes (e.g., "ID").
    term : str
        Term e.g. "202580".
    aid_year_column : str, default "AID_YEAR"
        Column in the Pell dataframe that stores aid year values.
    cohort_column : str, default "Cohort Name"
        Column in the retention dataframe that stores cohort names.

    Returns
    -------
    int
        The number of students who are both Pell recipients in the given aid year
        and cohort.

    Raises
    ------
    ValueError
        If any of the required column names are not present in their respective dataframes.
    """
    validate_pell_columns(df=dfp, id_column=id_column)
    validate_cohort_columns(df=dfr, id_column=id_column)

    aid_year = calc_academic_year_from_term(term)
    cohort = construct_cohort(term)
    # Filter IDs by aid year and cohort
    pids = dfp.loc[dfp[aid_year_column] == aid_year, id_column].dropna()
    rids = dfr.loc[dfr[cohort_column] == cohort, id_column].dropna()

    # Return overlap size
    return len(set(pids) & set(rids))


def grs_cohort(
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    cohort_column: str = "Cohort Name",
) -> int:
    """
    Calculate the total size of the provided cohort.

    Parameters
    ----------
    dfr : pandas.DataFrame
        Retention / cohort dataframe.
    id_column : str
        Column to use for student IDs; must exist in both dataframes (e.g., "ID").
    term : str
        Term e.g. "202580".
    cohort_column : str, default "Cohort Name"
        Column in the retention dataframe that stores cohort names.

    Returns
    -------
    int
        The number of students in the provided cohort.

    Raises
    ------
    ValueError
        If any of the required column names are not present in their respective dataframes.
    """
    validate_cohort_columns(df=dfr, id_column=id_column)

    cohort = construct_cohort(term)
    return sum(dfr[cohort_column] == cohort)


def total_headcount(dfe: pd.DataFrame, term: str, id_column: str) -> int:
    """
    Calculates enrollment headcount in the provided academic term for full-time, undergrad, degree-seeking students.

    Parameters
    ----------
    dfe : pandas.DataFrame
        The census data enrollment dataframe.
    term : str
        The term in which to calculate enrollment. (e.g., "202580").
    id_column: str
        The name of the id_column to identify unique students. (e.g., "ID").
    
    Returns
    -------
    int
        Returns the enrollment headcount for full-time, undergrad, degree-seeking students in the provide academic term.

    Raises
    ------
    ValueError
        If any of the required columns are not present in df.
    """
    validate_enrollment_columns(df=dfe, id_column=id_column)

    return dfe.loc[(
        (dfe['Academic Period'] == term) & 
        (dfe['Time Status'] == 'FT') & 
        (dfe['Student Level'] == 'UG') &
        (dfe['Degree'] != 'Non Degree')
    ), id_column].nunique()


def fall_enrollment(
    dfp: pd.DataFrame,
    dfr: pd.DataFrame,
    dfe: pd.DataFrame,
    id_column: str,
    term: str,
    pell: bool = False,
    transfer: bool = False
) -> int:
    """
    Term headcounts for full-time, degree-seeking undergrads.

    Headcount Options
    -----------------
    pell = False and transfer = False
        excludes incoming transfer students
    pell = True and transfer = False
        includes pell recipients and excludes incoming transfer students
    pell = False and transfer = True
        includes only incoming transfer students
    pell = True and transfer = True
        incoming transfer students that are also pell recipients

    Parameters
    ----------
    dfp : pandas.DataFrame
        Census Date Enrollment dataframe.
    dfe : pandas.DataFrame
        Census Date Enrollment dataframe.
    dfr : pandas.DataFrame
        Retention / cohort dataframe.
    id_column : str
        Column to use for student IDs; must exist in both dataframes (e.g., "ID").
    term: str
        Academic term (e.g. "202580")
    pell : bool
        If True, restrict to just pell recipients
    transfer: bool
        If True, include incoming transfer students, otherwise exclude them. 
        
    Returns
    -------
    int
        The number of total first-time students enrolled in the given term.

    Raises
    ------
    ValueError
        If any of the required column names are not present in their respective dataframes.
    """
    validate_pell_columns(df=dfp, id_column=id_column)
    validate_cohort_columns(df=dfr, id_column=id_column)
    validate_enrollment_columns(df=dfe, id_column=id_column)

    enrollment_conditions = (
        (dfe['Academic Period'] == term) &
        (dfe['Time Status'] == 'FT') &
        (dfe['Student Level'] == 'UG') &
        (dfe['Degree'] != 'Non Degree')
    )

    aid_year = calc_academic_year_from_term(term) 
    incoming_transfer_cohort = term[0:4] + " " + "Fall, Transfer, Full-Time"
    
    pids = dfp.loc[dfp['AID_YEAR'] == aid_year, id_column].dropna()
    eids = dfe.loc[enrollment_conditions, id_column].dropna()
    rids = dfr.loc[dfr['Cohort Name'] != incoming_transfer_cohort, id_column].dropna()
    rids_t = dfr.loc[dfr['Cohort Name'] == incoming_transfer_cohort, id_column].dropna()
    
    if not pell and not transfer:
        size = len(set(eids) & set(rids))
    elif pell and not transfer:
        size = len(set(pids) & set(eids) & set(rids))
    elif not pell and transfer:
        size = len(set(eids) & set(rids_t))
    else:
        size = len(set(pids) & set(eids) & set(rids_t))

    # Return overlap size
    return size
