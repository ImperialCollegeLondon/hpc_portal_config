# Modify a Gaussian input file in preparation for a portal job
# echo's the name of the checkpoint file that Gaussian will write

com_file=$1
fchk=$2

mem_mb=$(echo "$MEMORY_GB * 1024 * 0.9" | bc | xargs printf "%.0f")

top_link0() {
    # echo only the link0 directives from the top of the input script
    awk '{if ($1 ~ /^%/) {print $0} else {exit 0}}' "$1"
}

# strip out any existing resource directives
sed --in-place \
    --expression '/%Mem/Id' \
    --expression '/%CPU/Id' \
    --expression '/%NProcShared/Id' \
    --expression '/%GPUCPU/Id' \
    "$com_file"

# replace these 
sed --in-place \
    --expression "1s/^/%Mem=${mem_mb}MB\n/" \
    --expression "1s/^/%NProcShared=${NCORES}\n/" \
    "$com_file"

if [[ -n "${fchk}" ]]
then
    # chk file uploaded by user so make sure it is used by Gaussian
    # doesn't matter if OldChk and Chk are the same file
    chk=$(basename "$fchk" .fchk).chk
    sed --in-place --expression "1s/^/%OldChk=$chk\n/" "$com_file"
fi

if ! top_link0 "$com_file" | grep --ignore-case --quiet "%Chk"
then
    # no Chk directive so set this to a default value
    sed --in-place --expression "1s/^/%Chk=checkpoint.chk\n/" "$com_file"
    echo "checkpoint.chk"
else
    # print name of specified Chk file
    chk=$(grep --ignore-case --max-count=1 --only-matching --perl-regexp "%Chk=\K\S+" "$com_file")
    # ensure filename has the .chk suffix
    echo "$(basename "$chk" .chk).chk"
fi
