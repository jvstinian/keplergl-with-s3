import boto3  # noqa


def getKeysStartingWithPrefixToNextDelimiter(
    s3client, s3_bucket, key_prefix, target_token_index_in_key, include_contents=True, include_common_prefixes=True
):
    ret = []

    resp = s3client.list_objects(Bucket=s3_bucket, Prefix=key_prefix, Delimiter="/")
    LastMarker = None
    NextMarker = None

    while resp is not None:
        if include_contents and ("Contents" in resp):
            objs_info = resp["Contents"]
            for obj_info in objs_info:
                if "Key" in obj_info:
                    LastMarker = obj_info["Key"]
                    potential_data_set_id = obj_info["Key"].split("/")[target_token_index_in_key]
                    if potential_data_set_id not in ret:
                        ret.append(potential_data_set_id)

        if include_common_prefixes and ("CommonPrefixes" in resp):
            for prefix_info in resp["CommonPrefixes"]:
                if "Prefix" in prefix_info:
                    potential_data_set_id = prefix_info["Prefix"].split("/")[target_token_index_in_key]
                    if potential_data_set_id not in ret:
                        ret.append(potential_data_set_id)

        # Check to see if the response was truncated.
        if "IsTruncated" in resp and resp["IsTruncated"]:
            # If it was truncated, set the marker to start with in the next call to list_objects.
            if "NextMarker" in resp:
                NextMarker = resp["NextMarker"]
            else:
                print(
                    "Call to list_objects was truncated, but NextMarker not specified, so falling back to the last observed key per the documentation.  Perhaps try setting the delimiter?"
                )
                NextMarker = LastMarker
            resp = s3client.list_objects(Bucket=s3_bucket, Prefix=key_prefix, Marker=NextMarker, Delimiter="/")
        else:
            resp = None
    return ret
