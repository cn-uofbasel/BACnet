from Feed import Feed

yasmin = Feed("yasmin")
esther = Feed("esther")
vera = Feed("vera")

yasmin.generate()
esther.generate()
vera.generate()

yasmin.writeFollowToFeed("esther")
esther.writeFollowToFeed("yasmin")

yasmin.readFollowFromFeed()
esther.readFollowFromFeed()
vera.readFollowFromFeed()
