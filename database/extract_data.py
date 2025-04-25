import os
import re
import pandas as pd
import requests
import time
from tqdm import tqdm
import concurrent.futures

API_KEY = "5816543599e1a4ef936334337a385ecb"
BASE_URL = "https://api.themoviedb.org/3/movie/"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Số vòng fetch tối đa (và retry) cho cả movie details lẫn credits
MAX_FETCH_ROUNDS = 3

###############################################################################
# 1) Các hàm fetch đơn giản
###############################################################################
def simple_fetch_movie_details(tmdb_id):
    """
    Gọi API TMDB để lấy thông tin chi tiết phim, trả về dict JSON hoặc None nếu thất bại.
    """
    url = f"{BASE_URL}{tmdb_id}?api_key={API_KEY}&language=en-US"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def simple_fetch_credits(tmdb_id):
    """
    Gọi API TMDB để lấy thông tin credits (cast & crew), 
    trả về dict JSON hoặc None nếu thất bại.
    """
    url = f"{BASE_URL}{tmdb_id}/credits?api_key={API_KEY}&language=en-US"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

###############################################################################
# 2) Hàm xử lý dữ liệu
###############################################################################
def process_image_url(path):
    if path:
        return IMAGE_BASE_URL + path
    return None

def parse_movie_details(row):
    """
    Gọi simple_fetch_movie_details. Nếu thành công, trả về tuple:
      (movie_detail, genres_list, movie_genres_list, prod_companies_list, movie_companies_list).
    Ngược lại, trả về None.
    """
    tmdb_id = row["tmdbId"]
    details = simple_fetch_movie_details(tmdb_id)
    if not details:
        return None

    movie_detail = {
        "movieId": row["movieId"],
        "tmdbId": tmdb_id,
        "title": row["title"],  # Giữ title từ file gốc
        "budget": details.get("budget"),
        "original_language": details.get("original_language"),
        "original_title": details.get("original_title"),
        "overview": details.get("overview"),
        "poster_path": process_image_url(details.get("poster_path")),
        "release_date": details.get("release_date"),
        "revenue": details.get("revenue"),
        "runtime": details.get("runtime"),
        "status": details.get("status"),
    }

    # Genres
    genres = []
    movie_genres = []
    for g in details.get("genres", []):
        genres.append((g["id"], g["name"]))
        movie_genres.append({"movieId": row["movieId"], "genreId": g["id"]})

    # Production companies
    prod_companies = []
    movie_companies = []
    for pc in details.get("production_companies", []):
        prod_companies.append(
            (
                pc["id"],
                process_image_url(pc.get("logo_path")),
                pc["name"],
                pc.get("origin_country"),
            )
        )
        movie_companies.append(
            {"movieId": row["movieId"], "production_company_id": pc["id"]}
        )

    return (movie_detail, genres, movie_genres, prod_companies, movie_companies)

def parse_credits_data(movie_id, tmdb_id):
    """
    Gọi simple_fetch_credits cho 1 phim (movieId, tmdbId).
    Nếu thành công, trả về (list_people, list_credits).
    Ngược lại, trả về None.
    """
    data = simple_fetch_credits(tmdb_id)
    if not data:
        return None

    people_list = []
    credits_list = []

    # Cast
    for cast in data.get("cast", []):
        person_tuple = (
            cast["id"],
            cast.get("gender", 0),
            cast.get("known_for_department", ""),
            cast.get("name", ""),
            cast.get("original_name", ""),
            process_image_url(cast.get("profile_path")),
        )
        people_list.append(person_tuple)
        credits_list.append(
            {
                "movieId": movie_id,
                "personId": cast["id"],
                "role": "cast",
                "job": cast.get("character", ""),
            }
        )

    # Crew
    for crew in data.get("crew", []):
        person_tuple = (
            crew["id"],
            crew.get("gender", 0),
            crew.get("known_for_department", ""),
            crew.get("name", ""),
            crew.get("original_name", ""),
            process_image_url(crew.get("profile_path")),
        )
        people_list.append(person_tuple)
        credits_list.append(
            {
                "movieId": movie_id,
                "personId": crew["id"],
                "role": "crew",
                "job": crew.get("job", ""),
            }
        )

    return (people_list, credits_list)

###############################################################################
# 3) Fetch đa luồng (không retry vòng trong)
###############################################################################
def concurrent_fetch_movie_details(movies_df, max_workers=10):
    df = movies_df.reset_index(drop=True)
    results = [None] * len(df)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_i = {}
        for i, row in df.iterrows():
            future = executor.submit(parse_movie_details, row)
            future_to_i[future] = i

        for future in tqdm(
            concurrent.futures.as_completed(future_to_i),
            total=len(future_to_i),
            desc="Fetching Movie Details",
        ):
            i = future_to_i[future]
            try:
                results[i] = future.result()
            except Exception:
                results[i] = None

    return results

def concurrent_fetch_credits(movie_details_df, max_workers=10):
    df = movie_details_df.reset_index(drop=True)
    results = [None]*len(df)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_i = {}
        for i, row in df.iterrows():
            future = executor.submit(parse_credits_data, row["movieId"], row["tmdbId"])
            future_to_i[future] = i

        for future in tqdm(
            concurrent.futures.as_completed(future_to_i),
            total=len(future_to_i),
            desc="Fetching Credits",
        ):
            i = future_to_i[future]
            try:
                results[i] = future.result()
            except Exception:
                results[i] = None

    return results

###############################################################################
# 4) Multi-round fetch cho Movie Details và Credits
###############################################################################
def multi_round_fetch_movie_details(movies_df, max_rounds=3, max_workers=10):
    n = len(movies_df)
    final_results = [None] * n
    remaining_indices = set(range(n))

    for round_no in range(1, max_rounds+1):
        if not remaining_indices:
            break

        print(f"\n=== Movie Details Round {round_no}/{max_rounds} ===")
        print(f"Remaining movies: {len(remaining_indices)}")

        subset_df = movies_df.iloc[list(remaining_indices)].reset_index(drop=True)
        round_results = concurrent_fetch_movie_details(subset_df, max_workers=max_workers)

        success_this_round = 0
        for i_sub, res in enumerate(round_results):
            i_orig = list(remaining_indices)[i_sub]
            if res is not None:
                final_results[i_orig] = res
                success_this_round += 1

        newly_success = [idx for idx in remaining_indices if final_results[idx] is not None]
        for s in newly_success:
            remaining_indices.remove(s)

        print(f"Round {round_no} done. New successes: {success_this_round}")
        if success_this_round == 0:
            print("No additional success => stop fetching details.")
            break

    return final_results

def multi_round_fetch_credits(movie_details_df, max_rounds=3, max_workers=10):
    n = len(movie_details_df)
    final_results = [None]*n
    remaining_indices = set(range(n))

    for round_no in range(1, max_rounds+1):
        if not remaining_indices:
            break

        print(f"\n=== Credits Round {round_no}/{max_rounds} ===")
        print(f"Remaining movies for credits: {len(remaining_indices)}")

        subset_df = movie_details_df.iloc[list(remaining_indices)].reset_index(drop=True)
        round_results = concurrent_fetch_credits(subset_df, max_workers=max_workers)

        success_this_round = 0
        for i_sub, res in enumerate(round_results):
            i_orig = list(remaining_indices)[i_sub]
            if res is not None:
                final_results[i_orig] = res
                success_this_round += 1

        newly_success = [idx for idx in remaining_indices if final_results[idx] is not None]
        for s in newly_success:
            remaining_indices.remove(s)

        print(f"Credits Round {round_no} done. New successes: {success_this_round}")
        if success_this_round == 0:
            print("No additional success => stop fetching credits.")
            break

    return final_results

###############################################################################
# 5) Hàm refetch cho bất kỳ cột nào bị thiếu (ngoại trừ movieId & tmdbId)
###############################################################################
def fix_incomplete_movie_details(movie_details_df,
                                 original_movies_df,
                                 max_workers=5):
    """
    Rà soát TẤT CẢ cột (trừ movieId, tmdbId) của movie_details_df. 
    Nếu thiếu (NaN) ở cột nào, ta fetch lại API TMDB cho phim đó để cập nhật.
    
    TRẢ VỀ movie_details_df đã cập nhật
    """

    # 1) Xác định các cột cần check = tất cả cột trừ movieId, tmdbId
    columns_available = list(movie_details_df.columns)
    columns_to_check = [col for col in columns_available if col not in ("movieId","tmdbId")]

    print("\n=== Checking incomplete data for ALL columns: ", columns_to_check)

    # 2) Tạo mask cho các phim thiếu ít nhất 1 cột
    incomplete_mask = movie_details_df[columns_to_check].isna().any(axis=1)
    incomplete_df = movie_details_df[incomplete_mask].copy()

    if incomplete_df.empty:
        print("No incomplete movies found. Skipping fix_incomplete_movie_details.")
        return movie_details_df  # Không thay đổi gì, trả về DF gốc

    print(f"Found {len(incomplete_df)} incomplete movies. Attempting to refetch...")

    # 3) Đảm bảo có cột 'title' để parse (nếu parse_movie_details cần)
    needed_cols = ["movieId", "tmdbId", "title"]
    merged_incomplete = pd.merge(
        incomplete_df[["movieId","tmdbId"]],
        original_movies_df[needed_cols],
        on=["movieId","tmdbId"],
        how="left"
    )

    # 4) Tạo hàm fetch
    def fetch_missing_info(row):
        details = simple_fetch_movie_details(row["tmdbId"])
        if not details:
            return None

        new_data = {
            "title": row["title"],
            "budget": details.get("budget"),
            "original_language": details.get("original_language"),
            "original_title": details.get("original_title"),
            "overview": details.get("overview"),
            "poster_path": process_image_url(details.get("poster_path")),
            "release_date": details.get("release_date"),
            "revenue": details.get("revenue"),
            "runtime": details.get("runtime"),
            "status": details.get("status")
        }
        return (row["movieId"], new_data)

    # 5) Chạy đa luồng cho subset
    df_local = merged_incomplete.reset_index(drop=True)
    results = [None]*len(df_local)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_i = {}
        for i, row in df_local.iterrows():
            future = executor.submit(fetch_missing_info, row)
            future_to_i[future] = i

        for future in tqdm(concurrent.futures.as_completed(future_to_i),
                           total=len(future_to_i),
                           desc="Refetch Missing Info"):
            i = future_to_i[future]
            try:
                results[i] = future.result()
            except:
                results[i] = None

    # 6) Áp dụng kết quả trở lại movie_details_df
    updated_count = 0
    for item in results:
        if item is not None:
            movie_id, new_data = item
            for col, val in new_data.items():
                movie_details_df.loc[movie_details_df["movieId"] == movie_id, col] = val
            updated_count += 1

    print(f"Refetched & updated data for {updated_count} incomplete movies.")
    return movie_details_df  # TRẢ VỀ DF ĐÃ UPDATE

###############################################################################
# Hàm fix_csv: đọc file CSV, ghép những dòng bị tách, sau đó ghi đè với đúng format
###############################################################################
def fix_csv(input_file, output_file):
    """
    Đọc file CSV ban đầu và ghép các dòng bị tách thành 1 record hợp lệ.
    Giả định: record mới bắt đầu với:
      - dòng header ("movieId,")
      - hoặc chuỗi số + dấu phẩy ("^\d+,")
    Ghi ra file output_file.
    """
    with open(input_file, encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []
    current_line = None

    for line in lines:
        line = line.rstrip("\n")  # bỏ ký tự xuống dòng

        # Kiểm tra xem line có phải bắt đầu record mới hay header
        # Dùng regex: "^(movieId,)" hoặc "^\d+,"
        if re.match(r"^(movieId,)|(^\d+,)", line):
            # Nếu đang có record, push nó vào fixed_lines
            if current_line is not None:
                fixed_lines.append(current_line)
            current_line = line
        else:
            # Dòng đang nối tiếp record cũ
            if current_line is None:
                current_line = line
            else:
                current_line += " " + line

    # push record cuối
    if current_line is not None:
        fixed_lines.append(current_line)

    with open(output_file, "w", encoding="utf-8") as f:
        for l in fixed_lines:
            f.write(l + "\n")

    print(f"Đã fix xong format file CSV: {output_file}")

###############################################################################
# 6) main()
###############################################################################
def main():
    # Đọc file links.csv gốc
    links_df = pd.read_csv('links.csv')
    print("Original links.csv row count:", len(links_df))

    # Xử lý: loại bỏ các dòng thiếu tmdbId và giữ lại lần xuất hiện đầu tiên của tmdbId (loại bỏ trùng lặp)
    links_clean = links_df.dropna(subset=['tmdbId'])
    # Thông báo này (SettingWithCopyWarning) thường xuất hiện do pandas
    # ta có thể dùng .loc[:] hoặc copy() tường minh. Nhưng về logic, nó vẫn chạy được.
    links_clean = links_clean.copy()
    links_clean['tmdbId'] = links_clean['tmdbId'].astype(int)

    links_unique = links_clean.drop_duplicates(subset=['tmdbId'], keep='first')

    # Đọc file movies.csv
    movies_df = pd.read_csv('movies.csv')

    # Merge với dữ liệu links đã làm sạch theo cột movieId
    final_df = pd.merge(movies_df, links_unique[['movieId', 'tmdbId']], on='movieId', how='inner')

    # Lưu file kết quả (nếu cần)
    final_df.to_csv('movies_with_tmdb.csv', index=False)

    # In ra số lượng dòng sau khi xử lý
    print("Final merged dataset row count:", len(final_df))

    # Đọc file gốc
    original_df = pd.read_csv("movies_with_tmdb.csv")
    print(f"Total movies from original file: {len(original_df)}")

    # -------------------------
    # A) Fetch Movie Details (nhiều vòng)
    # -------------------------
    movie_results = multi_round_fetch_movie_details(
        original_df, max_rounds=MAX_FETCH_ROUNDS, max_workers=10
    )

    movie_details_list = []
    genres_set = set()
    movie_genres_list = []
    prod_companies_set = set()
    movie_companies_list = []

    for res in movie_results:
        if res is not None:
            md, g_list, mg_list, pc_list, mpc_list = res
            movie_details_list.append(md)
            genres_set.update(g_list)
            movie_genres_list.extend(mg_list)
            prod_companies_set.update(pc_list)
            movie_companies_list.extend(mpc_list)

    print(f"\n== DONE fetching movie details (max rounds={MAX_FETCH_ROUNDS}) ==")
    print(f"Successfully fetched details for {len(movie_details_list)} / {len(original_df)} movies.")

    # Tạo DataFrame
    movie_details_df = pd.DataFrame(movie_details_list)

    # -------------------------
    # B) Rà soát & refetch cho mọi cột thiếu (trừ movieId/tmdbId)
    # -------------------------
    movie_details_df = fix_incomplete_movie_details(
        movie_details_df,
        original_df,
        max_workers=5
    )

    # -------------------------
    # C) Fetch Credits (nhiều vòng)
    # -------------------------
    if not movie_details_df.empty:
        credit_results = multi_round_fetch_credits(
            movie_details_df[["movieId","tmdbId"]],
            max_rounds=MAX_FETCH_ROUNDS,
            max_workers=10
        )
        people_set = set()
        movie_credits_list = []
        for res in credit_results:
            if res is not None:
                pl, cl = res
                for p in pl:
                    people_set.add(p)
                movie_credits_list.extend(cl)
        credited_movie_ids = set([m["movieId"] for m in movie_credits_list])
        print(f"\n== DONE fetching credits => {len(credited_movie_ids)} movies have credits")
    else:
        # Nếu không có phim nào có details => credits = rỗng
        people_set = set()
        movie_credits_list = []

    # -------------------------
    # D) Tạo DataFrame & Lưu
    # -------------------------
    # 1) movie_details
    movie_details_df = movie_details_df.sort_values("movieId").reset_index(drop=True)

    # 2) genres
    genres_df = pd.DataFrame(list(genres_set), columns=["genreId","name"])\
                 .sort_values("genreId").reset_index(drop=True)
    movie_genres_df = pd.DataFrame(movie_genres_list, columns=["movieId","genreId"])\
                      .sort_values(["movieId","genreId"]).reset_index(drop=True)

    # 3) production companies
    prod_companies_df = pd.DataFrame(
        list(prod_companies_set),
        columns=["id","logo_path","name","origin_country"]
    ).sort_values("id").reset_index(drop=True)

    movie_companies_df = pd.DataFrame(movie_companies_list)\
                          .sort_values(["movieId","production_company_id"])\
                          .reset_index(drop=True)

    # 4) people + credits
    people_df = pd.DataFrame(
        list(people_set),
        columns=["personId","gender","known_for_department","name","original_name","profile_path"]
    ).sort_values("personId").reset_index(drop=True)

    movie_credits_df = pd.DataFrame(movie_credits_list)\
                       .sort_values(["movieId","personId"]).reset_index(drop=True)

    # Lưu file
    # Ghi tạm file movie_details để còn fix format
    movie_details_temp = "movie_details.csv"
    movie_details_df.to_csv(movie_details_temp, index=False)

    # E) Fix format cho movie_details.csv
    fix_csv("movie_details.csv", "movie_details_fixed.csv")

    # Đổi tên file fix -> file cũ
    os.remove("movie_details.csv")
    os.rename("movie_details_fixed.csv", "movie_details.csv")

    # Kiểm tra
    df_check = pd.read_csv("movie_details.csv")

    genres_df.to_csv("genres.csv", index=False)
    movie_genres_df.to_csv("movie_genres.csv", index=False)
    prod_companies_df.to_csv("production_companies.csv", index=False)
    movie_companies_df.to_csv("movie_production_companies.csv", index=False)
    people_df.to_csv("people.csv", index=False)
    movie_credits_df.to_csv("movie_credits.csv", index=False)

    print("\n===== ALL DONE =====")
    print(f"Movie details: {len(df_check)}")
    print(f"Genres: {len(genres_df)} - Movie-Genres: {len(movie_genres_df)}")
    print(f"Production companies: {len(prod_companies_df)} - Movie-Companies: {len(movie_companies_df)}")
    print(f"People: {len(people_df)}, Movie credits: {len(movie_credits_df)}")

if __name__ == "__main__":
    main()
