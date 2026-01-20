#!/usr/bin/env python3
"""
Find Canada collection ID in Media Cloud
"""

import mediacloud.api

API_KEY = '9e047cbfc9e1cd397857c21eb52c78902fc5f181'

print("="*80)
print("SEARCHING FOR CANADIAN MEDIA COLLECTIONS")
print("="*80)

# Initialize API
mc_search = mediacloud.api.SearchApi(API_KEY)
mc_directory = mediacloud.api.DirectoryApi(API_KEY)

try:
    print("\nSearching for collections with 'canada' or 'canadian'...\n")

    # Try to list collections
    collections = mc_directory.collection_list(name='canada')

    if collections:
        print(f"Response received")
        print("-"*80)

        # Debug: Check the structure
        print(f"\nDebug info: Response type = {type(collections)}")

        # If it's a dict, show its keys
        if isinstance(collections, dict):
            print(f"Dictionary keys: {list(collections.keys())}")
            print(f"\nFull response:")
            import json
            print(json.dumps(collections, indent=2, default=str))

            # Try to find collection data in the response
            if 'results' in collections:
                collection_list = collections['results']
            elif 'collections' in collections:
                collection_list = collections['collections']
            else:
                # The dict itself might be the collection data
                collection_list = [collections]
        elif isinstance(collections, list):
            collection_list = collections
        else:
            print(f"Unexpected type: {type(collections)}")
            collection_list = []

        if collection_list:
            print(f"\n\nFound {len(collection_list)} collection(s):")
            print("-"*80)
            for i, coll in enumerate(collection_list, 1):
                if isinstance(coll, dict):
                    print(f"\n{i}. Name: {coll.get('name', 'Unknown')}")
                    print(f"   ID: {coll.get('id', coll.get('collection_id', 'Unknown'))}")
                    print(f"   Sources: {coll.get('source_count', 'Unknown')}")
                    desc = coll.get('notes', None)
                    if desc:
                        print(f"   Description: {desc[:100]}...")
                else:
                    print(f"\n{i}. {coll}")
    else:
        print("No collections found with 'canada' in the name.")
        print("\nTrying broader search...")

        # Try without filter
        all_collections = mc_directory.collection_list()
        print(f"\nFound {len(all_collections)} total collections")

        # Filter for Canada-related
        if all_collections and len(all_collections) > 0:
            print("Showing first 10 collections as examples:")
            print("-"*80)
            for i, coll in enumerate(all_collections[:10], 1):
                if isinstance(coll, dict):
                    print(f"  {i}. {coll.get('name', 'Unknown')} (ID: {coll.get('id', 'Unknown')})")
                else:
                    print(f"  {i}. {coll}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*80)
    print("ALTERNATIVE APPROACH:")
    print("="*80)
    print("You can browse collections at: https://search.mediacloud.org/")
    print("Or search Canadian media sources directly using source filters.")