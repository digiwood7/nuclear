"""
핵의학Ⅰ(이론) PDF 추출 스크립트
PyMuPDF를 사용하여 텍스트, 이미지, 테이블 구조를 추출하고
Markdown 형식으로 변환합니다.
"""

import fitz  # PyMuPDF
import json
import os
import re
from pathlib import Path


def extract_page_text(page):
    """페이지에서 구조화된 텍스트를 추출합니다."""
    # 텍스트 블록 단위로 추출 (위치 정보 포함)
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)

    text_content = []
    for block in blocks.get("blocks", []):
        if block["type"] == 0:  # 텍스트 블록
            block_text = ""
            for line in block.get("lines", []):
                line_text = ""
                for span in line.get("spans", []):
                    line_text += span["text"]
                block_text += line_text + "\n"

            if block_text.strip():
                text_content.append({
                    "type": "text",
                    "content": block_text.strip(),
                    "bbox": block["bbox"],  # (x0, y0, x1, y1)
                    "font_size": _get_dominant_font_size(block),
                })
        elif block["type"] == 1:  # 이미지 블록
            text_content.append({
                "type": "image",
                "bbox": block["bbox"],
                "width": block.get("width", 0),
                "height": block.get("height", 0),
            })

    return text_content


def _get_dominant_font_size(block):
    """블록에서 가장 많이 사용된 폰트 크기를 반환합니다."""
    sizes = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            sizes.append(span.get("size", 12))
    if sizes:
        return max(set(sizes), key=sizes.count)
    return 12


def classify_heading(text, font_size, all_sizes):
    """폰트 크기를 기반으로 제목 레벨을 분류합니다."""
    if not all_sizes:
        return None

    avg_size = sum(all_sizes) / len(all_sizes)

    if font_size > avg_size * 1.5:
        return 1  # H1
    elif font_size > avg_size * 1.2:
        return 2  # H2
    elif font_size > avg_size * 1.05:
        return 3  # H3
    return None


def blocks_to_markdown(blocks, all_font_sizes):
    """추출된 블록들을 Markdown으로 변환합니다."""
    md_lines = []

    for block in blocks:
        if block["type"] == "image":
            md_lines.append(f"[이미지: {block['width']}x{block['height']}]")
            md_lines.append("")
        elif block["type"] == "text":
            content = block["content"]
            heading_level = classify_heading(
                content, block["font_size"], all_font_sizes
            )

            if heading_level and len(content) < 100:
                prefix = "#" * heading_level
                md_lines.append(f"{prefix} {content}")
            else:
                md_lines.append(content)
            md_lines.append("")

    return "\n".join(md_lines)


def extract_images(doc, page_idx, page, output_dir):
    """페이지에서 이미지를 추출하여 저장합니다."""
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    image_list = page.get_images(full=True)
    saved = []

    for img_idx, img in enumerate(image_list):
        xref = img[0]
        try:
            pix = fitz.Pixmap(doc, xref)
            if pix.n > 4:  # CMYK → RGB 변환
                pix = fitz.Pixmap(fitz.csRGB, pix)

            filename = f"page_{page_idx + 1:03d}_img_{img_idx + 1:02d}.png"
            filepath = os.path.join(images_dir, filename)
            pix.save(filepath)
            saved.append(filename)
        except Exception:
            pass

    return saved


def detect_chapters(pages_data):
    """페이지 데이터에서 챕터/섹션 구조를 감지합니다."""
    chapters = []
    current_chapter = {"title": "서론", "start_page": 1, "sections": []}

    # 큰 폰트로 된 짧은 텍스트를 챕터 제목으로 판별
    all_sizes = []
    for page in pages_data:
        for block in page.get("blocks", []):
            if block["type"] == "text":
                all_sizes.append(block["font_size"])

    if not all_sizes:
        return chapters

    avg_size = sum(all_sizes) / len(all_sizes)

    for page in pages_data:
        for block in page.get("blocks", []):
            if block["type"] != "text":
                continue
            content = block["content"].strip()
            if (block["font_size"] > avg_size * 1.4
                and len(content) < 80
                and len(content) > 2):
                if current_chapter["title"] != content:
                    if current_chapter.get("content"):
                        chapters.append(current_chapter)
                    current_chapter = {
                        "title": content,
                        "start_page": page["page_num"],
                        "sections": [],
                    }

    if current_chapter:
        chapters.append(current_chapter)

    return chapters


def main():
    pdf_path = "C:/src/nuclear/reference/TalkFile_핵의학Ⅰ(이론).pdf 2.pdf"
    output_dir = "C:/src/nuclear/output/extracted"

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "pages"), exist_ok=True)

    doc = fitz.open(pdf_path)
    total_pages = doc.page_count
    print(f"PDF 열기 완료: {total_pages} 페이지")

    # 전체 폰트 크기 수집 (제목 감지용)
    all_font_sizes = []
    pages_data = []

    # 1단계: 모든 페이지에서 텍스트 추출
    print("1단계: 텍스트 추출 중...")
    for i in range(total_pages):
        page = doc[i]
        blocks = extract_page_text(page)

        for b in blocks:
            if b["type"] == "text":
                all_font_sizes.append(b["font_size"])

        pages_data.append({
            "page_num": i + 1,
            "blocks": blocks,
        })

        if (i + 1) % 50 == 0:
            print(f"  ... {i + 1}/{total_pages} 페이지 처리됨")

    print(f"텍스트 추출 완료: {len(pages_data)} 페이지")

    # 2단계: 이미지 추출
    print("2단계: 이미지 추출 중...")
    total_images = 0
    for i in range(total_pages):
        page = doc[i]
        saved = extract_images(doc, i, page, output_dir)
        total_images += len(saved)

        if (i + 1) % 50 == 0:
            print(f"  ... {i + 1}/{total_pages} 페이지 이미지 처리됨")

    print(f"이미지 추출 완료: {total_images}개")

    # 3단계: 페이지별 Markdown 생성
    print("3단계: Markdown 변환 중...")
    full_markdown = []
    full_markdown.append("# 핵의학Ⅰ (이론)\n")
    full_markdown.append(f"> 총 {total_pages} 페이지\n")
    full_markdown.append("---\n")

    for page_data in pages_data:
        page_num = page_data["page_num"]
        blocks = page_data["blocks"]

        if not blocks:
            continue

        md = blocks_to_markdown(blocks, all_font_sizes)
        if md.strip():
            full_markdown.append(f"\n<!-- 페이지 {page_num} -->\n")
            full_markdown.append(md)

        # 페이지별 개별 파일도 저장
        page_md_path = os.path.join(
            output_dir, "pages", f"page_{page_num:03d}.md"
        )
        with open(page_md_path, "w", encoding="utf-8") as f:
            f.write(f"# 페이지 {page_num}\n\n{md}")

    # 전체 Markdown 파일 저장
    full_md_path = os.path.join(output_dir, "nuclear_medicine_1_full.md")
    with open(full_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_markdown))

    print(f"Markdown 저장 완료: {full_md_path}")

    # 4단계: 청킹용 JSON 생성 (RAG 파이프라인용)
    print("4단계: RAG용 청크 데이터 생성 중...")
    chunks = []
    current_chunk = {"text": "", "page_start": 1, "page_end": 1, "metadata": {}}

    for page_data in pages_data:
        page_num = page_data["page_num"]
        page_text = ""

        for block in page_data["blocks"]:
            if block["type"] == "text":
                page_text += block["content"] + "\n"

        page_text = page_text.strip()
        if not page_text:
            continue

        # 청크 크기 관리 (약 800자 단위)
        if len(current_chunk["text"]) + len(page_text) > 800:
            if current_chunk["text"].strip():
                chunks.append({
                    "id": len(chunks),
                    "text": current_chunk["text"].strip(),
                    "page_start": current_chunk["page_start"],
                    "page_end": current_chunk["page_end"],
                    "char_count": len(current_chunk["text"].strip()),
                })
            current_chunk = {
                "text": page_text + "\n",
                "page_start": page_num,
                "page_end": page_num,
            }
        else:
            if not current_chunk["text"]:
                current_chunk["page_start"] = page_num
            current_chunk["text"] += page_text + "\n"
            current_chunk["page_end"] = page_num

    # 마지막 청크 추가
    if current_chunk["text"].strip():
        chunks.append({
            "id": len(chunks),
            "text": current_chunk["text"].strip(),
            "page_start": current_chunk["page_start"],
            "page_end": current_chunk["page_end"],
            "char_count": len(current_chunk["text"].strip()),
        })

    chunks_path = os.path.join(output_dir, "chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"청크 생성 완료: {len(chunks)}개 청크")

    # 5단계: 통계 요약
    stats = {
        "total_pages": total_pages,
        "pages_with_text": sum(
            1 for p in pages_data
            if any(b["type"] == "text" for b in p["blocks"])
        ),
        "pages_without_text": sum(
            1 for p in pages_data
            if not any(b["type"] == "text" for b in p["blocks"])
        ),
        "total_images": total_images,
        "total_chunks": len(chunks),
        "avg_chunk_chars": (
            sum(c["char_count"] for c in chunks) // len(chunks) if chunks else 0
        ),
        "total_chars": sum(c["char_count"] for c in chunks),
    }

    stats_path = os.path.join(output_dir, "extraction_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n===== 추출 결과 요약 =====")
    print(f"총 페이지: {stats['total_pages']}")
    print(f"텍스트 페이지: {stats['pages_with_text']}")
    print(f"빈 페이지: {stats['pages_without_text']}")
    print(f"추출 이미지: {stats['total_images']}개")
    print(f"생성 청크: {stats['total_chunks']}개")
    print(f"평균 청크 크기: {stats['avg_chunk_chars']}자")
    print(f"총 텍스트: {stats['total_chars']}자")
    print(f"출력 경로: {output_dir}")

    doc.close()


if __name__ == "__main__":
    main()
