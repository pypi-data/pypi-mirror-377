
import requests
import json
from lht.util import csv
from lht.sflake import query as q
from lht.salesforce import ingest_bapi20 as ingest
import time

def upsert(session, access_info, sobject, query, field, batch_size=25000):
    """
    Upsert records to Salesforce using data from a SQL query executed against Snowflake.
    Processes records in batches to handle large datasets efficiently.
    
    Args:
        session: Snowflake session object
        access_info: Salesforce access credentials dictionary
        sobject: Salesforce object name (e.g., 'Account', 'Contact')
        query: SQL query string to execute against Snowflake
        field: External ID field name for upsert operation
        batch_size: Number of records to process per batch (default: 25000)
    """
    print("\n" + "="*100)
    print("🚀 STARTING SALESFORCE UPSERT WITH BATCH PROCESSING")
    print("="*100)
    print(f"📋 Parameters:")
    print(f"   - SObject: {sobject}")
    print(f"   - External ID Field: {field}")
    print(f"   - Batch Size: {batch_size:,} records per batch")
    print(f"   - SQL Query: {query[:100]}{'...' if len(query) > 100 else ''}")
    print(f"   - Instance URL: {access_info.get('instance_url', 'Not available')}")
    print("="*100)
    
    try:
        access_token = access_info['access_token']
        
        print("🔍 STEP 1: Getting total record count...")
        # First, get the total count of records to determine number of batches
        count_query = f"SELECT COUNT(*) as total_count FROM ({query})"
        count_result = session.sql(count_query).collect()
        total_records = count_result[0][0] if count_result else 0
        
        print(f"📊 Total records to process: {total_records:,}")
        
        if total_records == 0:
            print("⚠️ No records found to process")
            return None
        
        # Calculate number of batches needed
        num_batches = (total_records + batch_size - 1) // batch_size
        print(f"📦 Will process {total_records:,} records in {num_batches} batch(es) of up to {batch_size:,} records each")
        
        bulk_api_url = access_info['instance_url']+ f"/services/data/v62.0/jobs/ingest"
        print(f"🔗 Bulk API URL: {bulk_api_url}")

        # Job data template
        job_data_template = {
            "object": f"{sobject}",  # Specify the Salesforce object
            "operation": "upsert",  # Use upsert operation
            "externalIdFieldName": f"{field}",  # Field to use for upsert
            "lineEnding" : "CRLF"
        }

        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        
        all_job_info = []
        successful_batches = 0
        failed_batches = 0
        total_processed = 0

        # Process records in batches - query each batch separately
        for batch_num in range(num_batches):
            offset = batch_num * batch_size
            limit = batch_size
            
            print(f"\n🔍 STEP 2.{batch_num + 1}: Processing batch {batch_num + 1}/{num_batches}")
            print(f"📊 Batch range: records {offset + 1:,} to {min(offset + batch_size, total_records):,}")
            
            try:
                # Query only the records for this batch using LIMIT and OFFSET
                batch_query = f"{query} LIMIT {limit} OFFSET {offset}"
                print(f"🔍 Executing batch query: {batch_query[:100]}...")
                
                results = session.sql(batch_query).collect()
                
                # Convert results to the expected format
                batch_records = []
                for result in results:
                    record = {}
                    for key, value in result.asDict().items():
                        if value is None:
                            record[key] = ''
                        else:
                            record[key] = value
                    batch_records.append(record)
                
                actual_batch_size = len(batch_records)
                total_processed += actual_batch_size
                print(f"📊 Retrieved {actual_batch_size:,} records for this batch (Total processed: {total_processed:,}/{total_records:,})")
                
                if actual_batch_size == 0:
                    print("⚠️ No records in this batch, skipping...")
                    continue
                
                print("🔍 Converting batch records to CSV format...")
                batch_data = csv.json_to_csv(batch_records)
                print(f"📄 Batch CSV data length: {len(batch_data):,} characters")

                # Create a new job for this batch
                print("🔍 Creating Salesforce Bulk API job for this batch...")
                response = requests.post(bulk_api_url, headers=headers, data=json.dumps(job_data_template))
                
                if response.status_code != 200:
                    print(f"❌ Job creation failed with status {response.status_code}")
                    print(f"❌ Response: {response.text}")
                    response.raise_for_status()
                    
                job_info = response.json()
                print(f"✅ Job created successfully: {job_info}")
                job_id = job_info['id']
                print(f"🆔 Job ID: {job_id}")

                #########################################################
                ###  SEND BATCH FILE
                #########################################################
                print("🔍 Sending batch CSV data to Salesforce...")
                ingest.send_file(access_info, job_id, batch_data)
                print("✅ Batch file sent successfully")
                
                #########################################################
                ###  CLOSE JOB
                #########################################################
                print("🔍 Closing job to start processing...")
                close_results = ingest.job_close(access_info, job_id)
                print(f"✅ Job closed: {close_results}")

                #########################################################
                ###  CHECK STATUS
                #########################################################
                print("🔍 Monitoring batch job status...")
                status_check_count = 0
                batch_success = False
                
                while True:
                    status_check_count += 1
                    close_results = ingest.job_status(access_info, job_id)
                    print(f"📊 Status check #{status_check_count} - ID: {close_results['id']}, Status: {close_results['state']}")
                    
                    if close_results['state'] == 'JobComplete':
                        print("✅ Batch job completed successfully!")
                        batch_success = True
                        successful_batches += 1
                        break
                    elif close_results['state'] in ['Failed', 'Aborted']:
                        print(f"❌ Batch job failed with status: {close_results['state']}")
                        print(f"❌ Full job details: {close_results}")
                        failed_batches += 1
                        break
                    
                    print("⏳ Waiting 10 seconds before next status check...")
                    time.sleep(10)
                
                # Store job info for this batch
                batch_job_info = {
                    'batch_number': batch_num + 1,
                    'job_id': job_id,
                    'records_processed': actual_batch_size,
                    'success': batch_success,
                    'job_info': job_info
                }
                all_job_info.append(batch_job_info)
                
                print(f"✅ Batch {batch_num + 1} processing completed")
                
                # Clear batch_records from memory to free up space
                del batch_records
                del batch_data
                
            except Exception as batch_error:
                print(f"❌ Error processing batch {batch_num + 1}: {batch_error}")
                failed_batches += 1
                batch_job_info = {
                    'batch_number': batch_num + 1,
                    'job_id': None,
                    'records_processed': 0,
                    'success': False,
                    'error': str(batch_error)
                }
                all_job_info.append(batch_job_info)
                continue

        print("\n" + "="*100)
        print("✅ BATCH UPSERT PROCESSING COMPLETED")
        print("="*100)
        print(f"📊 Summary:")
        print(f"   - Total records: {total_records:,}")
        print(f"   - Records processed: {total_processed:,}")
        print(f"   - Total batches: {num_batches}")
        print(f"   - Successful batches: {successful_batches}")
        print(f"   - Failed batches: {failed_batches}")
        print(f"   - Success rate: {(successful_batches/num_batches)*100:.1f}%" if num_batches > 0 else "   - Success rate: N/A")
        print("="*100)
        
        return {
            'total_records': total_records,
            'records_processed': total_processed,
            'total_batches': num_batches,
            'successful_batches': successful_batches,
            'failed_batches': failed_batches,
            'batch_results': all_job_info
        }
        
    except Exception as e:
        print("\n" + "="*100)
        print("❌ UPSERT FAILED")
        print("="*100)
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Full traceback:")
        print(traceback.format_exc())
        print("="*100)
        raise

def update(session, access_info, sobject, query):
    access_token = access_info['access_token']

    #records = q.get_records(session, query)
    results = session.sql(query).collect()
    # Convert results to the expected format
    records = []
    for result in results:
        record = {}
        for key, value in result.asDict().items():
            if value is None:
                record[key] = ''
            else:
                record[key] = value
        records.append(record)

    data = csv.json_to_csv(records)

    bulk_api_url = access_info['instance_url']+ f"/services/data/v62.0/jobs/ingest"

    # Create a new job
    job_data = {
        "object": f"{sobject}",  # Specify the Salesforce object
        "operation": "update",  # Use upsert operation
        "lineEnding" : "CRLF"
    }

    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    # Create the job
    print("creating job")
    response = requests.post(bulk_api_url, headers=headers, data=json.dumps(job_data))
    job_info = response.json()
    #log_retl.job(session, job_info)

    job_id = job_info['id']

    #########################################################
    ###  SEND BATCH FILE
    #########################################################
    #def add_batch(instance_url, access_token, job_id, data):
    print("sending file")
    ingest.send_file(access_info, job_id, data)
    
    #########################################################
    ###  CLOSE JOB
    #########################################################
    print("closing job")
    close_results = ingest.job_close(access_info, job_id)
    print(close_results)


    #########################################################
    ###  CHECK STATUS
    #########################################################    
    while True:
        close_results = ingest.job_status(access_info, job_id)
        print("\nID: {}".format(close_results['id']))
        print("\nStatus: {}".format(close_results['state']))
        if close_results['state'] == 'JobComplete':
            break
        time.sleep(10)

    return job_info

def insert(session, access_info, sobject, query):
    access_token = access_info['access_token']

    records = q.get_records(session, query)
    data = csv.json_to_csv(records)

    bulk_api_url = access_info['instance_url']+ f"/services/data/v62.0/jobs/ingest"

    # Create a new job
    job_data = {
        "object": f"{sobject}",  
        "contentType" : "CSV",
        "operation": "insert",  
        "lineEnding" : "CRLF"
    }

    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    # Create the job
    print("creating job")
    response = requests.post(bulk_api_url, headers=headers, data=json.dumps(job_data))
    job_info = response.json()
    #log_retl.job(session, job_info)

    job_id = job_info['id']

    #########################################################
    ###  SEND BATCH FILE
    #########################################################
    #def add_batch(instance_url, access_token, job_id, data):
    print("sending file")
    ingest.send_file(access_info, job_id, data)
    
    #########################################################
    ###  CLOSE JOB
    #########################################################
    print("closing job")
    close_results = ingest.job_close(access_info, job_id)
    print(close_results)


    #########################################################
    ###  CHECK STATUS
    #########################################################    
    while True:
        close_results = ingest.job_status(access_info, job_id)
        print("\nID: {}".format(close_results['id']))
        print("\nStatus: {}".format(close_results['state']))
        if close_results['state'] == 'JobComplete':
            break
        time.sleep(10)

    return job_info

def delete(session, access_info, sobject, query, field):

    access_token = access_info['access_token']

    results = session.sql(query).collect()
    # Convert results to the expected format
    records = []
    for result in results:
        record = {}
        for key, value in result.asDict().items():
            if value is None:
                record[key] = ''
            else:
                record[key] = value
        records.append(record)
    data = csv.json_to_csv(records)

    bulk_api_url = access_info['instance_url']+ f"/services/data/v62.0/jobs/ingest"

    # Create a new job
    job_data = {
        "object": f"{sobject}",  
        "contentType" : "CSV",
        "operation": "delete", 
        "lineEnding" : "CRLF"
    }

    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    # Create the job
    print("creating job")
    response = requests.post(bulk_api_url, headers=headers, data=json.dumps(job_data))
    job_info = response.json()
    print("@@@ JOB: {}".format(job_info))
    #log_retl.job(session, job_info)

    job_id = job_info['id']

    #########################################################
    ###  SEND BATCH FILE
    #########################################################
    #def add_batch(instance_url, access_token, job_id, data):
    print("sending file")
    ingest.send_file(access_info, job_id, data)
    
    #########################################################
    ###  CLOSE JOB
    #########################################################
    print("closing job")
    close_results = ingest.job_close(access_info, job_id)
    print(close_results)


    #########################################################
    ###  CHECK STATUS
    #########################################################    
    while True:
        close_results = ingest.job_status(access_info, job_id)
        print("\nID: {}".format(close_results['id']))
        print("\nStatus: {}".format(close_results['state']))
        if close_results['state'] == 'JobComplete':
            break
        time.sleep(10)
    
    return job_info