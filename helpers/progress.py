books = [{"name": "Genesis", "chapters": 50}, {"name": "Exodus", "chapters": 40}]


def get_chapters_for_day(day, books, chapters_per_day=3):
    # Compute global chapter range (0-based)
    start = (day - 1) * chapters_per_day
    end = start + chapters_per_day

    # Flatten all chapters into a continuous sequence
    total_chapters = sum(book["chapters"] for book in books)
    if start >= total_chapters:
        return []  # no more chapters to send

    chapters_to_send = []
    current_index = 0

    for book in books:
        book_start = current_index
        book_end = current_index + book["chapters"]

        # Overlap check between this book’s range and our day’s range
        overlap_start = max(start, book_start)
        overlap_end = min(end, book_end)

        if overlap_start < overlap_end:
            # Compute actual chapter numbers within this book (1-based)
            first_chapter = overlap_start - book_start + 1
            last_chapter = overlap_end - book_start
            for chap in range(first_chapter, last_chapter + 1):
                chapters_to_send.append((book["name"], chap))

        current_index = book_end

        if current_index >= end:
            break
    return chapters_to_send


if __name__ == "__main__":
    chapters = get_chapters_for_day(17, books)
    message = "Readings for day 17:\n" + "\n".join([f"{b} {c}" for b, c in chapters])
    print(message)
