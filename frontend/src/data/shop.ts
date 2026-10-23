// Store facts shown on the site, taken from the catalogue in
// data/campus_customs.db (102 products after the Problem 2 cleanup).

export const FOUNDED = 1975
export const PRODUCT_COUNT = 102

export type Style = {
  slug: string
  name: string
  garmentTypes: string[]
}

// Groups the catalogue's 9 garment types into the styles shoppers filter by.
export const STYLES: Style[] = [
  { slug: 't-shirts', name: 'T-Shirts', garmentTypes: ['short-sleeve t-shirt'] },
  { slug: 'long-sleeves', name: 'Long Sleeves', garmentTypes: ['long-sleeve performance shirt', 'mockneck sweatshirt'] },
  { slug: 'crewnecks', name: 'Crewnecks', garmentTypes: ['crewneck sweatshirt'] },
  { slug: 'hoodies', name: 'Hoodies', garmentTypes: ['pullover hoodie', 'full-zip hoodie'] },
  { slug: 'quarter-zips', name: 'Quarter-Zips', garmentTypes: ['quarter-zip pullover'] },
  { slug: 'outerwear', name: 'Fleece & Outerwear', garmentTypes: ['full-zip fleece jacket', 'bomber jacket'] },
]

export function styleFor(garmentType: string) {
  return STYLES.find((style) => style.garmentTypes.includes(garmentType))
}

export type Collection = {
  name: string
  tag: string
  blurb: string
}

export const COLLECTIONS: Collection[] = [
  {
    name: 'Residential Colleges',
    tag: '11 colleges',
    blurb: 'Your college crest, front and center, from Benjamin Franklin to Trumbull.',
  },
  {
    name: 'Graduate & Professional Schools',
    tag: '11 schools',
    blurb: 'Law, Management, Medicine, Art, Music, and more, done in quiet, classic style.',
  },
  {
    name: 'Yale Athletics',
    tag: '17 sports',
    blurb: 'Left-chest classics for crew, squash, sailing, hockey, and every Bulldog team in between.',
  },
  {
    name: 'Yale Family',
    tag: 'Mom, Dad & more',
    blurb: 'For the parents, grandparents, aunts, and uncles cheering loudest from the stands.',
  },
  {
    name: 'Game Day & Vintage',
    tag: 'Rivalry & retro',
    blurb: 'The Game, Boola Boola, the Yale Bowl, and throwback bulldogs with plenty of attitude.',
  },
]
