from ibis import ir
from datetime import datetime
import hashlib

from ascend.application.context import ComponentExecutionContext
from ascend.common.events import log
from ascend.resources import ref, test, transform

@transform(
    inputs=[
        ref("read_longevity_all_data"),
    ],
    tests=[
        test("not_null", column="url"),
        test("not_null", column="article_text"),
        test("not_null", column="province_clean"),
        test("not_null", column="phrase_category_clean"),
        test("count_greater_than", count=0),
    ]
)
def cleaned_longevity_data(
    read_longevity_all_data: ir.Table,
    context: ComponentExecutionContext
) -> ir.Table:
    """
    Clean and validate longevity article data with comprehensive text validation.
    
    Args:
        read_longevity_all_data: Raw article data from Snowflake
        context: Component execution context
        
    Returns:
        Cleaned and validated article data
    """
    import ibis
    import ibis.expr.operations as ops
    
    # Get initial row count
    initial_count = read_longevity_all_data.count().execute()
    log(f"Starting with {initial_count} total rows")
    
    # Step 1: Remove NULL URLs and duplicates
    data = read_longevity_all_data.filter(read_longevity_all_data.url.notnull())
    after_null_filter = data.count().execute()
    log(f"After removing NULL URLs: {after_null_filter} rows ({initial_count - after_null_filter} removed)")
    
    # Deduplicate by URL (keep first occurrence)
    data = data.mutate(
        row_num=ibis.row_number().over(
            ibis.window(group_by=data.url, order_by=data.publish_date)
        )
    ).filter(lambda t: t.row_num == 0).drop("row_num")
    
    after_dedup = data.count().execute()
    log(f"After deduplication: {after_dedup} rows ({after_null_filter - after_dedup} duplicates removed)")
    
    # Step 2: Text Validation - Create validation flags
    data = data.mutate(
        # Clean article text first
        article_text_clean=data.article_text.strip(),
        
        # Validation checks
        has_min_chars=data.article_text.length() >= 200,
        has_min_words=data.article_text.re_replace(r'\s+', ' ').split(' ').length() >= 30,
        has_punctuation=(
            data.article_text.contains('.') | 
            data.article_text.contains('?')
        ),
        is_not_empty=(
            data.article_text.notnull() & 
            (data.article_text.strip() != '')
        )
    )
    
    # Create overall text_valid flag
    data = data.mutate(
        text_valid=(
            data.has_min_chars & 
            data.has_min_words & 
            data.has_punctuation & 
            data.is_not_empty
        )
    )
    
    # Count validation failures before filtering
    validation_summary = data.group_by(data.text_valid).aggregate(row_count=ibis._.count()).execute()
    invalid_count = validation_summary[validation_summary['text_valid'] == False]['row_count'].sum() if False in validation_summary['text_valid'].values else 0
    
    log(f"Text validation results:")
    log(f"  - Valid articles: {after_dedup - invalid_count}")
    log(f"  - Invalid articles (removed): {invalid_count}")
    
    # Filter to only valid articles
    data = data.filter(data.text_valid)
    
    # Drop intermediate validation columns
    data = data.drop(['has_min_chars', 'has_min_words', 'has_punctuation', 'is_not_empty'])
    
    after_validation = data.count().execute()
    log(f"After text validation: {after_validation} rows")
    
    # Step 3: Standardize Province Names
    data = data.mutate(
        province_clean=data.province.lower().contains('ontario').ifelse('Ontario',
            data.province.lower().contains('british columbia').ifelse('British Columbia',
            data.province.lower().contains('bc').ifelse('British Columbia',
            data.province.lower().contains('quebec').ifelse('Quebec',
            data.province.lower().contains('québec').ifelse('Quebec',
            data.province.lower().contains('alberta').ifelse('Alberta', 'Other'))))))
    )
    
    # Step 4: Clean Text Fields
    data = data.mutate(
        title=data.title.strip(),
        phrase=data.phrase.strip(),
        article_text=data.article_text_clean,
        
        # Clean and validate phrase_category
        phrase_category_clean=(data.phrase_category.lower().strip() == 'limiting').ifelse('limiting',
            (data.phrase_category.lower().strip() == 'neutral').ifelse('neutral',
            (data.phrase_category.lower().strip() == 'empowering').ifelse('empowering', 'neutral')))
    ).drop('article_text_clean')
    
    # Step 5: Date Standardization
    data = data.mutate(
        # Parse and standardize date
        publish_date=ibis.date(data.publish_date),
        year=ibis.date(data.publish_date).year(),
        month=ibis.date(data.publish_date).month()
    )
    
    # Step 6: Add Metadata
    data = data.mutate(
        ingestion_date=ibis.literal(datetime.now().date()),
        
        # Create row hash from URL + publish_date
        row_hash=ibis.literal('hash_').concat(
            data.url.hash().cast('string')
        )
    )
    
    # Final count
    final_count = data.count().execute()
    
    # Log summary
    log("=" * 60)
    log("CLEANING SUMMARY")
    log("=" * 60)
    log(f"Initial rows:                    {initial_count}")
    log(f"Removed (NULL URLs):             {initial_count - after_null_filter}")
    log(f"Removed (Duplicates):            {after_null_filter - after_dedup}")
    log(f"Removed (Invalid article text):  {invalid_count}")
    log(f"Final clean rows:                {final_count}")
    log(f"Total removed:                   {initial_count - final_count}")
    log(f"Retention rate:                  {(final_count/initial_count*100):.1f}%")
    log("=" * 60)
    
    return data