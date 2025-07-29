import type {
  DataTableSortItem as DataTableSortItemType,
} from 'vuetify'


export interface DataTableOptionsType {
  page: number
  itemsPerPage: number
  sortBy: DataTableSortItemType[]
}

export interface LessonType {
  seq: number
  date: string
  state: number
}

export interface QuizType {
  id: number
  lesson_id: number
  order: number
  answer: number | null
  content: string
  image_url: string | null
  state: number
  options: OptionType[]
}

export interface OptionType {
  id: number
  order: number
  content: string
  count: number | null
  is_selected: boolean | null
}

export interface ResponseType {
  id: number
  username: string
  quiz_id: number
  option_id: number
  option_order: number
}
