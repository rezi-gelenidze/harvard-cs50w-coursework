from .models import Bid, Listings, Comments, Watchlist

def format_price(floatprice):
    """ return formatted $n string"""
    return f'${floatprice:.2f}'


def get_price(listing_id):
    """
        check listing if they have bids and assign highest
        bid as price else leave starting bid as price
    """
    bids = Bid.objects.filter(listing_id=listing_id)
    if bids.exists():
        price = bids.order_by('bid').last().bid
    else:
        price = Listings.objects.get(pk=listing_id).price
    
    return format_price(price)


def shorten_text(text, text_type):
    """
    shorten title or description for
    displaying it on index page listings

    limit title to 80
    limit title to 400 if needed
    """
    if text_type == 'title':
        limit = 80
    elif text_type == 'description':
        limit = 400
    else:
        return None
        
    if len(text) <= limit:
        return text

    return f'{text[:limit]}...'
    

def validate_bid(bid, listing_id):
    try:
        bid = float(bid)
    except:
        return False

    bids = Bid.objects.filter(listing_id=listing_id)

    if bids.exists():
        highest = bids.order_by('bid').last().bid

        if not bid > highest:
            return False
    else:
        price = Listings.objects.get(pk=listing_id).price

        if not bid > price:
            return False
        
    return bid


def retrieve_listing(listing_id, user):
    try:
        listing = Listings.objects.get(pk=listing_id)
    except Listings.DoesNotExist:
        listing = None

    if listing:
        # if user is author and authenticated on active listing,
        # make 'close listing' available
        if user.is_authenticated and listing.seller == user and listing.active:
            closeable = True
        else:
            closeable = False

        listing.price = get_price(listing.pk)
        comments = Comments.objects.filter(post=listing_id)
        try:
            watchlisted = Watchlist.objects.get(listing_id=listing_id, user_id=user).watched
        except:
            watchlisted = False

        return  {
                'listing' : listing,
                'comments' : comments,
                'watching' : watchlisted,
                'closeable' : closeable
            }
    return None


def determine_winner(listing):
    bids = Bid.objects.filter(listing_id=listing)
    if bids:
        highest_bidder = bids.order_by('bid').last().bidder_id
        return highest_bidder
    return None