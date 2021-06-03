com_file=$1
fchk=$2

chk=$(basename "$fchk" .fchk).chk

# strip out any existing resource directives
sed -i  -e '/%Mem/d' \
    -e '/%CPU/d' \
    -e '/%NProcShared/d' \
    -e '/%GPUCPU/d' \
    "$com_file"

# replace these 
sed -i -e "1s/^/%Mem=${MEMORY_GB}GB\n/" \
    -e "1s/^/%NProcShared=${NCPUS}\n/" \
    "$com_file"

if [[ -n "${fchk}" ]]
then
    # chk file uploaded by user so make sure it is used by Gaussian
    # doesn't matter if OldChk and Chk are the same file
    sed -i -e "1s/^/%OldChk=$chk\n/" "$com_file"
fi

if ! grep -q "%Chk" "$com_file"
then
    # no Chk directive so set this to a default value
    sed -i -e "1s/^/%Chk=checkpoint.chk\n/" "$com_file"
    echo "checkpoint.chk"
else
    # print name of specified Chk file
    grep -oP "%Chk=\K\S+" "$com_file"
fi
