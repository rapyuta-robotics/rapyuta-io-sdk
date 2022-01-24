#!/bin/sh

set +x

pipenv install --dev

pipenv run pip3 install coverage
pipenv run coverage run --source=rapyuta_io sdk_test/run_rio_sdk_test.py
pipenv run coverage report
pipenv run coverage html

if [ -z "${MINIO_ALIAS}" ]
then
 exit 0
fi

SDK_TEST_COVERAGE_FILE="sdk_test_coverage_$(date --iso-8601=sec)"
mc alias set "${MINIO_ALIAS}" "${MINIO_SERVER_URL}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}"

if ! (mc ls "${MINIO_ALIAS}" | grep -q "${MINIO_BUCKET}")
then
 echo "creating bucket ...."
 mc mb "${MINIO_ALIAS}/${MINIO_BUCKET}"
fi

cp -R "htmlcov" "${SDK_TEST_COVERAGE_FILE}"
tar -cvzf "${SDK_TEST_COVERAGE_FILE}.tar.gz" "${SDK_TEST_COVERAGE_FILE}"
echo "uploading coverage report ...."
mc cp "${SDK_TEST_COVERAGE_FILE}.tar.gz" "${MINIO_ALIAS}/${MINIO_BUCKET}"
SDK_TEST_REPORT_URL="$(mc share download "${MINIO_ALIAS}/${MINIO_BUCKET}/${SDK_TEST_COVERAGE_FILE}.tar.gz" | sed -n 's/^Share: //p')"
curl -X POST -H "Content-type: application/json" "${SLACK_INCOMING_WEBHOOK_URL}" --data '{"text": "'"${SDK_TEST_REPORT_URL}"'"}'

rm -rf SDK_TEST_COVERAGE_FILE
rm "${SDK_TEST_COVERAGE_FILE}.tar.gz"
