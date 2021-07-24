com_file="$1"
chk_file="$2"

log_file=$(basename "$com_file" "${com_file##*.}")log

export obabel="/apps/ood/openbabel/bin/obabel"

check_single_file() {
    # look for files with a suffix given by $1
    # if there is a single file echo the name
    # if there are multiple files we don't know what to use so echo an error to stderr
    shopt -s nullglob
    files=( *."$1" )
    if [ ${#files[@]} -eq 1 ]
    then
	echo "${files[0]}"
    elif [ ${#files[@]} -gt 1 ]
    then
	>&2 echo "Multiple *.${1} files found, unable to publish"
    fi
}

(
    echo -e "name\tdescription"
    echo -e "${com_file}\tGaussian input file"

    echo -e "${log_file}\tGaussian log file"

    fchk_file=$(basename "$chk_file" "${chk_file##*.}")fchk
    echo -e "${fchk_file}\tFormatted checkpoint file"

    wfn_file=$(check_single_file wfn)
    [ -n "$wfn_file" ] && echo -e "${wfn_file}\tWavefunction file"

    wfx_file=$(check_single_file wfx)
    [ -n "$wfx_file" ] && echo -e "${wfx_file}\tExtended-Wavefunction file"


    $obabel -i g03 "${log_file}" -o cml -O opt.cml && cml_file=opt.cml
    [ -n "$cml_file" ] && echo -e "${cml_file}\tOptimised geometry"

) > FILES_TO_PUBLISH

(
    echo -e "name\tvalue"
    gibbs=$(grep "Sum of electronic and thermal Free Energies=" "${log_file}" | tail -1 | awk ' {print $8}')
    [ -n "$gibbs" ] && echo -e "Gibbs Energy\t${gibbs}"
    inchi=$($obabel -i g03 "${log_file}" -o inchi)
    [ -n "$inchi" ] && echo -e "InChI\t${inchi}"
    inchikey=$($obabel -i g03 "${log_file}" -o inchikey)
    [ -n "$inchikey" ] && echo -e "InChIKey\t${inchikey}"
) > METADATA
