# ------------------------------------------------------------
# Fırsat listesi
# ------------------------------------------------------------
st.subheader("🔥 En Güçlü Sinyaller")

if posts:
    rows = []

    for p in posts:
        points = int(p.get("points") or p.get("score") or 0)
        comments = int(p.get("comments") or 0)

        if points < min_points:
            continue

        rows.append({
            "Başlık": (p.get("title") or "")[:80],
            "Kaynak": p.get("source", ""),
            "Puan": points,
            "Yorum": comments,
            "URL": p.get("url", ""),
        })

    if rows:

        df = (
            pd.DataFrame(rows)
            .sort_values("Puan", ascending=False)
            .head(top_n)
            .copy()
        )

        # Streamlit JSON hatasını önlemek için
        df["Puan"] = df["Puan"].astype(int)
        df["Yorum"] = df["Yorum"].astype(int)

        st.dataframe(
            df,
            hide_index=True,
            width="stretch",
            column_config={
                "URL": st.column_config.LinkColumn("Link"),
                "Puan": st.column_config.ProgressColumn(
                    "Puan",
                    min_value=0,
                    max_value=int(max(df["Puan"].max(), 1)),
                    format="%d",
                ),
            },
        )

        st.subheader("📊 Puan Dağılımı (Top)")
        chart_df = df.set_index("Başlık")[["Puan"]]
        st.bar_chart(chart_df)

    else:
        st.warning("Filtrelere uyan sinyal yok.")

else:
    st.warning("Sinyal verisi yok.")
