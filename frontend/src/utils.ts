import { LOCALE } from '@/constants'


export function formatDate (datetime: string) {
  const date = new Date(datetime)
  const formattedDate = date.toLocaleDateString(LOCALE)
  return formattedDate
}

export function formatTime (datetime: string) {
  const date = new Date(datetime)
  const formattedTime = date.toLocaleTimeString(LOCALE)
  return formattedTime
}

export function formatDatetime (datetime: string) {
  const formattedDate = formatDate(datetime)
  const formattedTime = formatTime(datetime)
  return `${formattedDate} ${formattedTime}`
}
